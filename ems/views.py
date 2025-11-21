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
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
import uuid
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import *
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
import base64
from django.core.files.base import ContentFile
from rest_framework.exceptions import APIException

# from core.common import get_financial_year, get_fy_month_year
from django.http import JsonResponse
from .models import *
from .serializer import *
import random
import string
from django.db import transaction
import os
from cards.mypaginations import MyPageNumberPagination

# Function to generate OTP 
from .models import CustomUser, OTPRecord  # Assuming you have these models defined

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

            # Compose email content
            recipients = [email]
            email_body = render_to_string('RegistrationOTP.html', {'email': email, 'otp_code': otp,'recipient_name':fullname,'support_email':support_email,})
            plain_message = strip_tags(email_body)

            print("otp--", otp)

            # Send mail using send_mail
            send_mail(
                subject='One-Time Password (OTP) Verification',
                message=plain_message,  # Plain text message
                from_email=os.environ.get('EMAIL_HOST_USER', 'mohitetechcube@gmail.com'),  # Ensure EMAIL_HOST_USER is correctly fetched
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

        try:
            otp_record = OTPRecord.objects.get(token=token, email=email)
        except OTPRecord.DoesNotExist:
            return JsonResponse({'error': 'Invalid token or email!'},)
        
        try:
            print("otp_entered==",otp_entered,otp_record.otp)
            if otp_entered == otp_record.otp:
                print("first")
                # OTP is correct, hash the password and create user 
                refferal = CustomUser.objects.filter(referalcode = referralCode).first()
                referalcode = generate_unique_referral_code()
                hashed_password = make_password(password)

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
    # permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.select_related('created_by','modified_by','deleted_by').filter(is_deleted=False).order_by('-id')
    serializer_class = CustomUserSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['usertype', 'email', 'mobilenumber','fullname','school_name']
 
    def get_queryset(self):
        queryset = self.queryset.filter()
        return queryset

class PutUserDetails(APIView):
    # permission_classes = [IsAuthenticated]
    
    def put(self,request,pk,format=None): 
        instance = CustomUser.objects.get(id=pk) 
        serializer = CustomUserSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(bkp_modified_by=request.user.username.upper(), modified_by_id=request.user.id, modified_at=timezone.now())
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            print("User serializer.errors", serializer.errors)
            return Response({"status": "error", "data": serializer.errors},)

class DeleteUserDetails(APIView):
    # permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data['data'] 
        for i in data:   
            CustomUser.objects.filter(id=i).update(is_deleted=True,deleted_by=request.user.id,bkp_deleted_by=request.user.username.upper(),deleted_at=timezone.now()) 
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