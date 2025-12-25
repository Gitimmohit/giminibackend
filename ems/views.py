from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from .serializer import *
from cards.models import *
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
import uuid
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import *
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
import base64
from django.core.files.base import ContentFile
from rest_framework.exceptions import APIException
from decouple import config
# from core.common import get_financial_year, get_fy_month_year
from django.http import JsonResponse
from .models import *
from .serializer import *
from cards.serializer import *
import random
import string
from django.db import transaction
import os
from .models import CustomUser, OTPRecord 
from cards.mypaginations import MyPageNumberPagination
from core.utils import hitby_user 
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404

from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.shortcuts import get_object_or_404
from django.db.models import (
    Count, Sum, DecimalField, Value, Case, When
)
from django.db.models.functions import TruncMonth, Cast

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ems.models import *

# for the duplicate
class CheckDuplicateEmail(APIView):
    def post(self, request):
        print("request===",request.data)
        email = request.data.get('email')
        exclude_email = request.query_params.get('exclude',None)  # "CURRENT" email to exclude
        update_id = request.data.get('user_ids',None) 
        is_updating = request.query_params.get('is_updating',False) 
        filter_wise = request.data.get('filter_wise',False) 
        is_updating_str = False if str(is_updating).lower() == "false" else True
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        filters ={}
        exclude_user ={}

        # if account wise filter 
        
        if update_id:
            exclude_user['id'] = update_id

        user_query = CustomUser.objects.filter(email__iexact=email,**filters).exclude(**exclude_user)

              
        total_email = user_query.count()
        print("total_email ====",total_email)   

        if total_email >= 1 and exclude_email and not is_updating_str:
            return Response({"duplicate": True, "message": "Email already exists"}, status=status.HTTP_200_OK)
        
        elif total_email >= 1 and is_updating_str:
            return Response({"duplicate": True, "message": "Email already exists"}, status=status.HTTP_200_OK)
        
        elif total_email and exclude_email != "CURRENT":
            return Response({"duplicate": True, "message": "Email already exists"}, status=status.HTTP_200_OK)
        
        return Response({"duplicate": False, "message": "Email is available"}, status=status.HTTP_200_OK)




# for the otp 

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

class SendOTPAPIView(APIView):
    def post(self, request):
        print("REQUEST data===", request.data)

        # Extract email and username
        email = request.data.get('email')
        fullname = request.data.get('fullname')
        support_email = "info@giminiplanatoriam.com"
        

        # Validate email and username
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        print("EMAIL====", email)

        # Check if the email already exists
        if CustomUser.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists! Please use another email or login.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP and token
        otp = generate_otp()
        token = uuid.uuid4()

        try:
            # Store OTP and token in the database within an atomic transaction
            with transaction.atomic():
                # if otp is already their then then delete first and then create 
                OTPRecord.objects.filter(email=email).delete()

                OTPRecord.objects.create(email=email, token=token, otp=otp)
                print("otp-",otp)
            # Compose email content
            recipients = [email]
            email_body = render_to_string('RegistrationOTP.html', {'email': email, 'otp_code': otp,'recipient_name':fullname,'support_email':support_email,})
            plain_message = strip_tags(email_body)


            # Send mail using send_mail
            send_mail(
                subject='One-Time Password (OTP) Verification',
                message=plain_message,  # Plain text message
                from_email=config('EMAIL_HOST_USER'),  # Ensure EMAIL_HOST_USER is correctly fetched
                recipient_list=[email],
                fail_silently=False,
                html_message=email_body  # HTML message
            )

            print("TOKEN=", token)
            return Response({'message': 'OTP sent successfully!', 'token': token}, status=status.HTTP_200_OK)

        except Exception as e:
            # Catch all exceptions to avoid server crash
            print(f"Error sending OTP: {e}")
            return Response({'error': 'Failed to send OTP, please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# for referral code 

def generate_unique_referral_code():
    characters = string.ascii_uppercase + string.digits  # A-Z + 0-9
    
    while True:
        code = ''.join(random.choices(characters, k=10))  # 10-character alphanumeric
        
        if not CustomUser.objects.filter(referalcode=code).exists():
            return code

class VerifyOTPAPIView(APIView):
    def post(self, request):
        print("verify request data===",request.data) 
        email = request.data.get('email')
        otp_entered = request.data.get('otp')
        token = request.data.get('token')
        password = request.data.get('password')
        referralCode = request.data.get('referralCode')
        school_name = request.data.get('school_name')
        fullname = request.data.get('fullname')
        usertype = request.data.get('usertype')
        dob = request.data.get('dob')
        mobilenumber = request.data.get('mobilenumber')
        refered_code = request.data.get('refered_code',None)

        try:
            otp_record = OTPRecord.objects.get(token=token, email=email)
        except OTPRecord.DoesNotExist:
            return JsonResponse({'error': 'Invalid token or email!'},)
        
        try:
            print("otp_entered==",otp_entered,otp_record.otp)
            if otp_entered == otp_record.otp:
                print("first",referralCode)
                # OTP is correct, hash the password and create user 
                refferal = CustomUser.objects.filter(referalcode = referralCode).first()
                referalcode = generate_unique_referral_code()
                hashed_password = make_password(password)
                print("refferal",refferal)
                CustomUser.objects.create(
                    email=email, 
                    password=hashed_password,
                    mobilenumber=mobilenumber,
                    referalcode=referalcode,
                    reffered_by_id = refferal.id if refferal else None,
                    school_name=school_name,
                    fullname=fullname,
                    dob=dob,
                    usertype=usertype,
                    refered_code = refered_code
                    )
                print("second")
                
                # Delete OTP record from the database
                otp_record.delete()
                
                return Response({'message': 'User created successfully!', }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP! Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================ this is the login view ok 
class GetLoginToken(APIView):
    def post(self, request):
        try:
            print("request.user", request.data)
            user = CustomUser.objects.filter(email__iexact=request.data.get("username"), is_deleted=False).first()
            print("user=====", user)
            serialized_user = CustomUserSerializer(user).data
            password = request.data.get("password")
            channel_access = request.data.get("channel_access")
            if user is not None and user.check_password(password):
                if user.is_active: 
                    if user.first_login:
                        refresh = RefreshToken.for_user(user)
                        context = {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                            'first_login': str(True), 
                            'user_data':serialized_user,
                        }
                        return Response(context, status.HTTP_200_OK)
                    else:
                        refresh = RefreshToken.for_user(user)
                        context = {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                            'first_login': str(False), 
                            'user_data':serialized_user,
                        }
                        user.last_login = timezone.now()
                        user.save()
                        return Response(context, status.HTTP_200_OK) 
                else:
                    context = {
                        "message": "Please verify your account first!"
                    }
                    return Response(context, status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            else:
                context = {
                    "detail": "No active account found with the given credentials"
                }
                return Response(context, status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print("Exception:", str(e)) 
            # Handle the exception here
            raise APIException(detail=str(e))
        

class GetUserInfo(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            print("request.user", request.data)
            user = CustomUser.objects.filter(email__iexact=request.data.get("username"), is_deleted=False).first()
            print("user=====", user)
            serialized_user = CustomUserSerializer(user).data
            if user is not None:
                if user.is_active: 
                    if user.first_login:
                        refresh = RefreshToken.for_user(user)
                        context = {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                            'first_login': str(True), 
                            'user_data':serialized_user,
                        }
                        return Response(context, status.HTTP_200_OK)
                    else:
                        refresh = RefreshToken.for_user(user)
                        context = {
                            'refresh': str(refresh),
                            'access': str(refresh.access_token),
                            'first_login': str(False), 
                            'user_data':serialized_user,
                        }
                        user.last_login = timezone.now()
                        user.save()
                        return Response(context, status.HTTP_200_OK) 
                else:
                    context = {
                        "message": "Please verify your account first!"
                    }
                    return Response(context, status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            else:
                context = {
                    "detail": "No active account found with the given credentials"
                }
                return Response(context, status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print("Exception:", str(e)) 
            raise APIException(detail=str(e))
   

class GetUserDetails(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.select_related('created_by','modified_by','deleted_by').filter(is_deleted=False).order_by('-id')
    serializer_class = CustomUserSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['usertype', 'email', 'mobilenumber','fullname','school_name']
 
    def get_queryset(self):
        request_from= self.request.query_params.get('from')
        filters = {}
        if request_from == "referral":
            filters['reffered_by'] = self.request.user.id


        queryset = self.queryset.filter(**filters)
        return queryset

class PutUserDetails(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk,format=None): 
        modified_by, bkp_modified_by = hitby_user(self,request) 
        data = request.data
        refered_inst = CustomUser.objects.filter(refered_code = request.data.get('refered_code',None)).first()
        
        CustomUser.objects.filter(id=pk).update(
            reffered_by_id=refered_inst.id if refered_inst else None,
            refered_code = request.data.get('refered_code',None)
        )
        
        instance = CustomUser.objects.get(id=pk) 
        if request.data.get('is_approved') and not instance.reffered_amt_credit:
            data['reffered_amt_credit'] = True
            
        serializer = CustomUserSerializer(instance, data=data, partial=True)
        if instance.reffered_by and not instance.reffered_amt_credit:
            reffer_instance = CustomUser.objects.filter(id=instance.reffered_by.id).first()
            total_refferal = CustomUser.objects.filter(reffered_by_id=instance.reffered_by.id,reffered_amt_credit = True, usertype = 'PROMOTER').count() 
            if reffer_instance.usertype == "STUDENT" and instance.usertype == "STUDENT":
                print("first")
                transaction_amt = 25
                Transactions.objects.create(user_id = reffer_instance.id,
                                           request_type="CR",
                                           current_status = "APPROVED",
                                           request_time = timezone.now(),
                                           transaction_amt = transaction_amt,
                                           transaction_from = "REFFERAL",
                                           created_by = modified_by,
                                           bkp_created_by = bkp_modified_by,
                                           )
                
                # add in wallet also 
                wallet = Wallet.objects.filter(user_id= instance.reffered_by.id).first()
                
                if wallet:
                    wallet.current_wallet_amount = wallet.current_wallet_amount + transaction_amt
                    wallet.earn_amount = wallet.earn_amount + transaction_amt
                    wallet.save()
                else:
                    Wallet.objects.create(
                        user_id= instance.reffered_by.id,
                        earn_amount = transaction_amt,
                        current_wallet_amount=transaction_amt,
                        created_at=timezone.now(),
                    )
                
            elif reffer_instance.usertype == "PROMOTER" and instance.usertype == "PROMOTER" :
                # according to the pay stucture
                print("total_refferal",total_refferal)
                ref_amnt = 25
                if total_refferal > 1500 and total_refferal <= 3499 :
                    ref_amnt = 35
                if total_refferal > 3500 and total_refferal <= 4999 :
                    ref_amnt = 45
                if total_refferal > 5000 :
                    ref_amnt = 50

                Transactions.objects.create(user_id = reffer_instance.id,
                                           request_type="CR",
                                           current_status = "APPROVED",
                                           request_time = timezone.now(),
                                           transaction_amt = ref_amnt,
                                           transaction_from = "REFFERAL",
                                           created_by = modified_by,
                                           bkp_created_by = bkp_modified_by,
                                           )

                # add in wallet also 
                wallet = Wallet.objects.filter(user= instance.reffered_by).first()
                
                if wallet:
                    wallet.current_wallet_amount = wallet.current_wallet_amount + ref_amnt
                    wallet.earn_amount = wallet.earn_amount + ref_amnt
                    wallet.save()
                else:
                    Wallet.objects.create(
                        user= instance.reffered_by,
                        earn_amount = ref_amnt,
                        current_wallet_amount=ref_amnt,
                        created_at=timezone.now(),
                    )

        if serializer.is_valid():

            serializer.save(modified_by=modified_by, bkp_modified_by=bkp_modified_by, modified_at=timezone.now())
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            print("User serializer.errors", serializer.errors)
            return Response({"status": "error", "data": serializer.errors},)

class DeleteUserDetails(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data['data'] 
        deleted_by, bkp_deleted_by = hitby_user(self,request) 
        for i in data:   
            CustomUser.objects.filter(id=i).update(is_deleted=True,deleted_by=deleted_by,bkp_deleted_by=bkp_deleted_by,deleted_at=timezone.now()) 
        return Response(status=status.HTTP_200_OK)
    
class Add_LoginDetail(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        try:
            print("login data====", request.data)
            username = request.data.get('username')
            user = CustomUser.objects.get(username=username)
            print("user======", user)
            f_data = request.data
            f_data['user'] = user.id
            f_data['logintime'] = timezone.now()
            
            serializer = LoginDetailSerializer(data=f_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User with the provided username does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Print the exception message
            print("Exception:", str(e)) 
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    permission_classes= [IsAuthenticated] 
    def post(self, request):
        try:
            print("Logout Request data is", request.data)
            refresh_token = request.data["refresh_token"]
            print("request.user.id", request.user.id)
            latest_login = LoginDetail.objects.filter(user=request.user.id).order_by('-login_time').first()
            print("latest_login---", latest_login)
            if latest_login:
                latest_login.logout_time = timezone.now()
                latest_login.save()

            token = RefreshToken(refresh_token) 
            token.blacklist()
            
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print("exception", str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        
class ResetPassword(APIView):
    """
    An endpoint for changing password.
    """
    def put(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(username=request.data.get('username'), is_deleted=False)
        except CustomUser.DoesNotExist:
            return Response("User not found", status=404)
        
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        
        if not user.check_password(old_password):
            return Response("Old Password is incorrect", status=400)
        
        user.set_password(new_password)
        user.first_login = False
        user.password_changed_date = timezone.now()
        user.password_changed_by = user.username
        user.password_changed = True
        user.save()
        
        return Response("Password reset successfully", status=200)

  
class CheckUsername(APIView): 
    def get(self, request):
        user_name = request.query_params.get('username')
        if CustomUser.objects.filter(username__iexact=user_name, is_deleted=False).exists():
            return Response({'status': 'error', 'message': 'Duplicate Entry'})
        else:
            return Response({'status': 'success', 'message': 'No duplicates found'})

        
class CheckUserEmail(APIView):
    def get(self, request):
        user_email = request.query_params.get('email')
        if CustomUser.objects.filter(email=user_email, is_deleted=False).exists():
            return Response({'status': 'error', 'message': 'Duplicate Entry'})
        else:
            return Response({'status': 'success', 'message': 'No duplicates found'})


class CheckUserPhone(APIView): 
    def get(self, request):
        user_phone = request.query_params.get('phone')
        if CustomUser.objects.filter(mobilenumber=user_phone, is_deleted=False).exists():
            return Response({'status': 'error', 'message': 'Duplicate Entry'})
        else:
            return Response({'status': 'success', 'message': 'No duplicates found'})
        
# views.py
class SendForgotPasswordOTPView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'status': 'error', 'message': 'Email is required'}, status=400)

        try:
            user = CustomUser.objects.get(email=email, is_active=True)
            if not user.email:  # Double check (just in case)
                raise ValueError()
        except (CustomUser.DoesNotExist, ValueError):
            return Response({'status': 'error','message': 'No account found with this email.'}, status=400)

        # Delete old OTP
        OTPRecord.objects.filter(email=email).delete()
        # Generate & Save OTP
        otp = ''.join(random.choices(string.digits, k=6))
        OTPRecord.objects.create(email=email, otp=otp,token=uuid.uuid4())

        # Send Email (Safe Method)
        try:
            html_message = render_to_string('forgot_otp.html', {
                'otp': otp,
                'name': (user.fullname.title() if user.fullname else "User") 
            })
            send_mail(
                subject="Your Secure Password Reset OTP",
                message=strip_tags(html_message),
                from_email="OTP Team",
                recipient_list=[email],
                fail_silently=False,
                html_message=html_message,
            )
        except Exception as e:
            print("Email failed:", e)

        return Response({'status': 'success','message': 'OTP sent to your email!'})


class ResetPasswordWithOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('newPassword')
        confirm_password = request.data.get('confirmPassword')

        if new_password != confirm_password:
            return Response({'status': 'error', 'message': 'Passwords do not match'}, status=400)
        if len(new_password) < 8:
            return Response({'status': 'error', 'message': 'Password must be 8+ characters'}, status=400)

        try:
            record = OTPRecord.objects.get(email=email, otp=otp)
            user = CustomUser.objects.get(email=email)

            user.set_password(new_password)
            user.password_changed = True
            user.password_changed_date = timezone.now()
            user.save()

            record.delete()
            return Response({'status': 'success', 'message': 'Password changed successfully!'})

        except OTPRecord.DoesNotExist:
            return Response({'status': 'error', 'message': 'Invalid or expired OTP'}, status=400)
        except CustomUser.DoesNotExist:
            return Response({'status': 'error', 'message': 'User not found'}, status=400)
        
class AddUserBankDetails(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):  
        user = request.data.get('user',None)  
        bank_instance = BankDetails.objects.filter(user_id = user).first()
        if bank_instance :
            serializer = BankDetailsSerializer(bank_instance,data=request.data, partial=True)
        else:
            serializer = BankDetailsSerializer(data=request.data, partial=True)
        if serializer.is_valid(): 
            serializer.save(created_by_id=request.user.id,bkp_created_by=request.user.fullname.upper() if request.user.fullname else None, created_at=timezone.now(), )
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "error", "data": serializer.errors})
        
class GetUserBankDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user', None)  
        bank_details = BankDetails.objects.filter(user_id=user_id).first()  

        serializer = BankDetailsSerializer(bank_details)
        return Response({"status": "success", "data": serializer.data},status=status.HTTP_200_OK)




class GetDashboardDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get("user")
        filter_type = request.query_params.get("filter_type")

        if not user_id:
            return Response({"error": "user parameter is required"}, status=400)

        # ---------- USER ----------
        user = get_object_or_404(CustomUser, id=user_id)

        filters = {}
        performance_data = []

        # ---------- STUDENT ----------
        if filter_type == "STUDENT":
            filters["usertype"] = "STUDENT"

        # ---------- SALES (NEW – ONLY ADDITION) ----------
        if filter_type == "SALES":
            filters["usertype"] = "PROMOTER"

            today = datetime.now()
            current_month_start = today.replace(day=1)
            last_3_month_start = (today - relativedelta(months=3)).replace(day=1)

            # 🔹 Current month referrals
            referral_count_month = CustomUser.objects.filter(
                reffered_by_id=user_id,
                usertype="PROMOTER",
                created_at__gte=current_month_start
            ).count()

            # 🔹 Total active promoters
            total_active_promoters = CustomUser.objects.filter(
                reffered_by_id=user_id,
                usertype="PROMOTER",
                is_active=True
            ).count()

            

            # 🔹 Monthly referral performance
            referral_qs = (
                CustomUser.objects
                .filter(
                    reffered_by_id=user_id,
                    usertype="PROMOTER",
                    created_at__gte=last_3_month_start
                )
                .annotate(month=TruncMonth("created_at"))
                .values("month")
                .annotate(referral=Count("id"))
            )

            referral_dict = {
                r["month"].strftime("%b"): r["referral"]
                for r in referral_qs
            }

            performance_data = []
            for i in range(3, -1, -1):
                month_date = today - relativedelta(months=i)
                month_name = month_date.strftime("%b")

                performance_data.append({
                    "month": month_name,
                    "referral": referral_dict.get(month_name, 0),
                    "target": 100,  # static target
                })

        # ---------- PROMOTER (UNCHANGED) ----------
        if filter_type == "PROMOTER":
            filters["usertype"] = "STUDENT"

            today = datetime.now()
            start_date = (today - relativedelta(months=3)).replace(day=1)

            referral_qs = (
                CustomUser.objects
                .filter(
                    reffered_by_id=user_id,
                    usertype="STUDENT",
                    created_at__gte=start_date
                )
                .annotate(month=TruncMonth("created_at"))
                .values("month")
                .annotate(referrals=Count("id"))
            )

            referral_dict = {
                r["month"].strftime("%b"): r["referrals"]
                for r in referral_qs
            }

            clean_amount = Case(
                When(transaction_amt__isnull=True, then=Value(0)),
                When(transaction_amt__iexact="none", then=Value(0)),
                When(transaction_amt="", then=Value(0)),
                default=Cast(
                    "transaction_amt",
                    DecimalField(max_digits=10, decimal_places=2)
                ),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )

            earnings_qs = (
                Transactions.objects
                .filter(
                    user=user,
                    created_at__gte=start_date,
                    transaction_from="REFFERAL",
                    is_deleted=False
                )
                .annotate(
                    month=TruncMonth("created_at"),
                    clean_amt=clean_amount
                )
                .values("month")
                .annotate(earnings=Sum("clean_amt"))
            )

            earnings_dict = {
                e["month"].strftime("%b"): e["earnings"] or 0
                for e in earnings_qs
            }

            performance_data = []
            for i in range(3, -1, -1):
                month_date = today - relativedelta(months=i)
                month_name = month_date.strftime("%b")

                performance_data.append({
                    "month": month_name,
                    "referrals": referral_dict.get(month_name, 0),
                    "earnings": float(earnings_dict.get(month_name, 0)),
                })

        # ---------- TOTAL REFERRALS ----------
        referral_count = CustomUser.objects.filter(
            reffered_by_id=user_id,
            **filters
        ).count()

        # 🔹 Recent 5 referrals
        recent_5_referrals = list(
            CustomUser.objects.filter(
                reffered_by_id=user_id,
                **filters
            )
            .order_by("-created_at")[:5]
            .values("id", "fullname", "is_active","created_at")
        )

        # ---------- WALLET ----------
        wallet = Wallet.objects.filter(user=user).first()
        current_wallet_amount = wallet.current_wallet_amount if wallet else 0
        earn_amount = wallet.earn_amount if wallet else 0

        # Upcoming 5 quizzes
        quiz_qs = Quiz.objects.filter(
            is_deleted=False,
            is_completed=False,
            quiz_date__gte=timezone.now()
        ).order_by("quiz_date")[:5]

        quiz_serializer = QuizSerializer(quiz_qs, many=True)

        # ---------- RESPONSE ----------
        return Response({
            "user_id": user.id,
            "referalcode": user.referalcode,
            "total_referrals": referral_count,

            # SALES only extras
            "total_referrals_current_month": referral_count_month if filter_type == "SALES" else 0,
            "total_active_promoters": total_active_promoters if filter_type == "SALES" else 0,
            "recent_5_referrals": recent_5_referrals,

            "current_wallet_amount": float(current_wallet_amount or 0),
            "earn_amount": float(earn_amount or 0),
            "performanceData": performance_data,

            "upcoming_quizzes": quiz_serializer.data,
        })
