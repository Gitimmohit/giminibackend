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