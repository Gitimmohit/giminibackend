from .models import * 
from .serializer import *
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.utils import timezone
from core.utils import hitby_user
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter 
from cards.mypaginations import MyPageNumberPagination
from rest_framework import status
from cards.models import Wallet
from decimal import Decimal
from django.shortcuts import get_object_or_404
class AddInvestmentScheme(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print("AddInvestmentScheme REQUEST DATA==", request.data) 
        if request.data.get('scheme_type') == "FIXED":
            investment_amount = request.data.get('investment_amount')
            duration_months = request.data.get('duration_months')

            exists = InvestmentScheme.objects.filter(
                scheme_type="FIXED",
                investment_amount=investment_amount,
                duration_months=duration_months,
                is_deleted=False
            ).exists()

            if exists:
                return Response(
                    {
                        "message": "Fixed investment scheme with this amount and duration already exists."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            min_amount = request.data.get('min_amount')
            max_amount = request.data.get('max_amount')
            interest_type = request.data.get('interest_type')

            exists = InvestmentScheme.objects.filter(
                scheme_type="PERCENTAGE",
                min_amount=min_amount,
                max_amount=max_amount,
                interest_type=interest_type,
                is_deleted=False
            ).exists()

            if exists:
                return Response(
                    {
                        "message": "Percentage investment scheme with this minimum, maximum amount and interest type in already exists."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = InvestmentSchemeSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(created_by_id=request.user.id,bkp_created_by=request.user.email, created_at=timezone.now())
            print("InvestmentScheme SERIALIZER DATA====",serializer.data)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print("InvestmentScheme SERIALIZER ERROR====",serializer.errors)
            return Response({"status": "error", "data": serializer.errors})
 
class GetInvestmentScheme(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = InvestmentScheme.objects.select_related('created_by','modified_by','deleted_by').filter(is_deleted=False).order_by('-id')
    serializer_class = InvestmentSchemeSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['scheme_type', 'interest_type', 'investment_amount', 'return_amount', 'duration_months']


class PutInvestmentScheme(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request,pk,format=None):
        print("PutInvestmentScheme======= ",request.data) 
        if request.data.get('scheme_type') == "FIXED":
            investment_amount = request.data.get('investment_amount')
            duration_months = request.data.get('duration_months')

            exists = InvestmentScheme.objects.filter(
                scheme_type="FIXED",
                investment_amount=investment_amount,
                duration_months=duration_months,
                is_deleted=False
            ).exclude(id=pk).exists()

            if exists:
                return Response(
                    {
                        "message": "Fixed investment scheme with this amount and duration already exists."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            min_amount = request.data.get('min_amount')
            max_amount = request.data.get('max_amount')
            interest_type = request.data.get('interest_type')

            exists = InvestmentScheme.objects.filter(
                scheme_type="PERCENTAGE",
                min_amount=min_amount,
                max_amount=max_amount,
                interest_type=interest_type,
                is_deleted=False
            ).exclude(id=pk).exists()

            if exists:
                return Response(
                    {
                        "message": "Percentage investment scheme with this minimum, maximum amount and interest type in already exists."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        instance = InvestmentScheme.objects.get(id=pk)
        serializer = InvestmentSchemeSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(bkp_modified_by=request.user.email, modified_by_id=request.user.id, modified_at=timezone.now())
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            print("InvestmentScheme serializer.errors", serializer.errors)
            return Response({"status": "error", "data": serializer.errors},)

class DeleteInvestmentScheme(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        deleted_by, bkp_deleted_by = hitby_user(self,request) 
        data = request.data['data'] 
        for i in data:  
            # Soft delete InvestmentScheme
            InvestmentScheme.objects.filter(id=i).update(is_deleted=True,deleted_by=deleted_by,bkp_deleted_by=bkp_deleted_by,deleted_at=timezone.now()) 
        return Response(status=status.HTTP_200_OK)

class AddInvestment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("AddInvestment REQUEST DATA==", request.data)

        serializer = UserInvestmentSerializer(
            data=request.data,
            context={"request": request}
        )

        if not serializer.is_valid():
            print("Investment SERIALIZER ERROR====", serializer.errors)
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():

                investment = serializer.save(user=request.user)
                wallet = Wallet.objects.select_for_update().get(
                    user=request.user
                )
                invested_amount = Decimal(investment.invested_amount)
                if wallet.current_wallet_amount < invested_amount:
                    return Response(
                        {
                            "status": "error",
                            "message": "Insufficient wallet balance"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                wallet.current_wallet_amount -= invested_amount
                wallet.save()

                return Response(
                    {
                        "status": "success",
                        "data": UserInvestmentSerializer(investment).data
                    },
                    status=status.HTTP_201_CREATED
                )

        except Wallet.DoesNotExist:
            return Response(
                {"status": "error", "message": "Wallet not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            print("e==", e)
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class GetInvestment(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserInvestmentSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['invested_amount', 'status', 'investment_amount']

    def get_queryset(self):
        user = self.request.user

        queryset = UserInvestment.objects.select_related('user').order_by('-id')

        # if admin → return all
        if user.usertype == 'SUPPER USER':
            return queryset

        # else → user-wise data
        return queryset.filter(user=user)

class PutApprovedInvestmentScheme(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, pk, format=None):

        investment = get_object_or_404(UserInvestment, id=pk)

        #  Only Admin Can Approve
        if not request.user.is_superuser:
            return Response(
                {"status": False, "message": "Only admin can approve investment"},
                status=status.HTTP_403_FORBIDDEN
            )

        old_status = investment.status
        old_withdraw_status = investment.withdraw_status

        serializer = UserInvestmentSerializer(
            investment,
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            return Response({
                "status": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        updated_investment = serializer.save(
            bkp_modified_by=request.user.email,
            modified_by_id=request.user.id,
            modified_at=timezone.now()
        )

        if old_status != "APPROVED" and updated_investment.status == "APPROVED":

            # Avoid duplicate commission
            already_generated = ReferralCommission.objects.filter(
                investment=updated_investment
            ).exists()

            if not already_generated:
                generate_referral_commission(updated_investment)

        # =====================================================
        if (
            old_withdraw_status != "WITHDRAWN"
            and updated_investment.withdraw_status == "WITHDRAWN"
        ):

            penalty = updated_investment.calculate_penalty()

            updated_investment.penalty_amount = penalty
            updated_investment.is_withdrawn = True
            updated_investment.withdrawn_at = timezone.now()
            updated_investment.save()

            # Stop Future Commission
            stop_commission_on_withdrawal(updated_investment.user)

            # Deactivate User ID
            user = updated_investment.user
            user.waiting_period_end = timezone.now() + timedelta(days=90)
            user.is_active_id = False
            user.save()

            return Response({
                "status": True,
                "message": "Investment Withdrawn Successfully",
                "penalty": str(penalty)
            }, status=status.HTTP_200_OK)

        return Response({
            "status": True,
            "message": "Investment Updated Successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


def generate_referral_commission(investment):

    user = investment.user
    amount = investment.invested_amount

    configs = {
        c.level: c for c in ReferralCommissionConfig.objects.all()
    }

    current_upline = user.reffered_by
    level = 1

    while current_upline and level <= 10:

        config = configs.get(level)
        if not config:
            break

        if current_upline.usertype != "ASTRO WEALTH":
            current_upline = current_upline.reffered_by
            level += 1
            continue

        if not current_upline.is_active:
            current_upline = current_upline.reffered_by
            level += 1
            continue

        if current_upline.total_direct < config.min_direct_required:
            current_upline = current_upline.reffered_by
            level += 1
            continue

        commission_amount = (
            amount * config.percentage
        ) / Decimal("100")

        commission_obj, created = ReferralCommission.objects.get_or_create(
            user=current_upline,
            from_user=user,
            investment=investment,
            level=level,
            defaults={
                "percentage": config.percentage,
                "commission_amount": commission_amount,
                "payout_month": timezone.now().date().replace(day=1)
            }
        )

        # ==========================
        # WALLET UPDATE LOGIC
        if created:  # avoid duplicate wallet credit

            wallet, _ = Wallet.objects.get_or_create(
                user=current_upline
            )

            wallet.earn_amount += commission_amount
            wallet.current_wallet_amount += commission_amount
            wallet.save()

        current_upline = current_upline.reffered_by
        level += 1

def stop_commission_on_withdrawal(user):
    """
    Stop commission generation when user withdraws investment
    """

    # Mark all APPROVED investments as withdrawn
    UserInvestment.objects.filter(
        user=user,
        status="APPROVED"
    ).update(
        withdraw_status="WITHDRAWN",
        is_withdrawn=True,
        withdrawn_at=timezone.now()
    )

    # Deactivate all active commissions generated from this user
    ReferralCommission.objects.filter(
        from_user=user,
        is_active=True
    ).update(
        is_active=False,
        stopped_at=timezone.now()
    )

class GetLevelWiseReferralEarningView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user_id = request.query_params.get("user")

        # --------------------------------------------------
        # CASE 1 → If specific user passed
        # --------------------------------------------------
        if user_id:
            user = get_object_or_404(CustomUser, id=user_id)

            level_data = ReferralCommission.objects.filter(
                user=user
            ).values("level").annotate(
                total_earning=Sum("commission_amount"),
                total_users=Count("from_user", distinct=True)
            ).order_by("level")

            total_earning = ReferralCommission.objects.filter(
                user=user
            ).aggregate(
                total=Sum("commission_amount")
            )["total"] or 0

            return Response({
                "status": True,
                "type": "single_user",
                "user_id": user.id,
                "user_name": user.fullname,
                "level_wise_income": level_data,
                "total_referral_income": total_earning
            })

        # --------------------------------------------------
        # CASE 2 → If NO user param → return ALL USERS DATA
        # --------------------------------------------------
        all_data = ReferralCommission.objects.values(
            "user__id",
            "user__fullname",
            "level"
        ).annotate(
            total_earning=Sum("commission_amount"),
            total_users=Count("from_user", distinct=True)
        ).order_by("user__id", "level")

        return Response({
            "status": True,
            "type": "all_users",
            "data": all_data
        })