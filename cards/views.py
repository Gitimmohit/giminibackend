from django.core.mail import EmailMultiAlternatives
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from .serializer import *
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter 
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import *
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
import base64
import os

from django.core.files.base import ContentFile
from datetime import timedelta ,time
from django.utils import timezone
from .mypaginations import MyPageNumberPagination
from django.db.models import F
# from core.common import get_financial_year, get_fy_month_year
from django.http import JsonResponse
from .models import * 
from ems.models import * 
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import io
from django.views.generic.base import RedirectView
from django.shortcuts import get_object_or_404
from core.utils import hitby_user
from django.db import transaction
 
class AddContactDetails(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print("AddContactDetails REQUEST DATA==", request.data) 
        name=request.data['name']

        qr_logo_doc = request.data.get('qr_logos')
        if qr_logo_doc:
            format, imgstr = qr_logo_doc.split(';base64,')
            ext = format.split('/')[-1]
            doc = ContentFile(base64.b64decode(imgstr), name=f'{name}qr_logo.{ext}')
            request.data['qr_logo'] = doc
        else:
            request.data['qr_logo'] = None
        # Set valid_upto date to one year from the current date
        valid_upto_date = timezone.now() + timedelta(days=365) 
        request.data['valid_upto'] = valid_upto_date

        serializer = ContactDetailsSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(created_by_id=request.user.id,bkp_created_by=request.user.username.upper(), created_at=timezone.now())
            print("ContactDetails SERIALIZER DATA====",serializer.data)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print("ContactDetails SERIALIZER ERROR====",serializer.errors)
            return Response({"status": "error", "data": serializer.errors})
 
class GetContactDetails(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ContactDetails.objects.select_related('created_by','modified_by','deleted_by').filter(is_deleted=False).order_by('-id')
    serializer_class = ContactDetailsSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'email', 'user__username', 'phone_number', 'company_name', 'designation']
 
    def get_queryset(self):
        queryset = self.queryset.filter(valid_upto__gte=timezone.now().date())
        return queryset


class PutContactDetails(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request,pk,format=None):
        print("PutContactDetails======= ",request.data) 
        instance = ContactDetails.objects.get(id=pk)
        name=request.data['name']
        serializer = ContactDetailsSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(bkp_modified_by=request.user.username.upper(), modified_by_id=request.user.id, modified_at=timezone.now())
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            print("ContactDetails serializer.errors", serializer.errors)
            return Response({"status": "error", "data": serializer.errors},)

class AddQuestions(APIView):
    permission_classes=[IsAdminUser]
    def post(self,request):
        try:
            serializers=QuestionsSerializer(data=request.data)
            if serializers.is_valid():
                with transaction.atomic():
                    serializers.save()
                    return Response({"status":"success","data":serializers.data},status=status.HTTP_200_OK)
            else:
                return Response({
                    "status":"serializer Error",
                    "details":serializers.errors
                },status=status.HTTP_400_BAD_REQUEST)   
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )         
 
class UpdateQuestion(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk, format=None):
        try:
            # Get instance
            try:
                instance = Questions.objects.get(id=pk)
            except Questions.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Question not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = QuestionsSerializer(instance, data=request.data, partial=True)

            if serializer.is_valid():
                with transaction.atomic():
                    serializer.save()

                return Response(
                    {"status": "success", "data": serializer.data},
                    status=status.HTTP_200_OK
                )

            return Response(
                {"status": "serializer error", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetQuestion(ListAPIView):
    queryset = Questions.objects.filter(is_deleted=False)
    serializer_class = QuestionsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # get today's date
        today = timezone.now().date()

        # Apply base queryset + valid_upto filter
        queryset = self.queryset.filter(valid_upto__gte=today)

        return queryset
             
class DeleteQuestion(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            try:
                instance = Questions.objects.get(id=pk)
            except Questions.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Question not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            with transaction.atomic():
                instance.delete()

            return Response(
                {"status": "success", "message": "Question deleted successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class AddPayment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print("AddContactDetails REQUEST DATA==", request.data) 
        data=request.data
        user = request.data.get('user',None)
        data['current_status'] = "PENDING"
        
        transactions_instance = Transactions.objects.filter(is_first_transaction = True,user_id = user).first()
        if transactions_instance :
            serializer = TransactionsSerializer(transactions_instance,data=request.data, partial=True)
        else:
            serializer = TransactionsSerializer(data=request.data, partial=True)

        if serializer.is_valid():
            CustomUser.objects.filter(id = user).update(
                is_payment = True,
                first_payment = "DONE"
            )

            serializer.save(
                created_by_id=request.user.id,
                bkp_created_by=request.user.fullname.upper() if request.user.fullname else None, 
                created_at=timezone.now(),
                request_time = timezone.now(),
                )
            print("ContactDetails SERIALIZER DATA====",serializer.data)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            print("ContactDetails SERIALIZER ERROR====",serializer.errors)
            return Response({"status": "error", "data": serializer.errors})


class FirstPayment(ListAPIView):
    queryset = Transactions.objects.filter(is_first_transaction=True)
    serializer_class = TransactionsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        # Apply base queryset + valid_upto filter
        queryset = self.queryset.filter(user_id=self.request.user.id)

        return queryset
class AddQuestionDetails(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            created_by, bkp_created_by = hitby_user(self,request)   
            serializer = QuestionsSerializer(data=request.data)
            if serializer.is_valid():
                question_instance = serializer.save(created_by=created_by,bkp_created_by=bkp_created_by, created_at=timezone.now()) 
                return Response({"message": "Question added successfully!","data": serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": "Something went wrong!","details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetQuestionsDetails(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Questions.objects.select_related('user','created_by','modified_by','deleted_by').filter(is_deleted=False).order_by('-id')
    serializer_class = QuestionsSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['question', 'answare', 'age_grup', 'option1', 'option2']
 
    def get_queryset(self):
        queryset = self.queryset.filter()
        return queryset
    
class GetQuestionsTransfer(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Questions.objects.select_related('user','created_by','modified_by','deleted_by').filter(is_deleted=False).order_by('-id')
    serializer_class = QuestionsSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['question']
    def get_queryset(self):
        queryset = super().get_queryset() 
        if self.request.GET['data'] != "all":
            data = Quiz.objects.filter(id=self.request.GET['data']).all()
            id_list = list(data.values_list('question__id', flat=True))
            id_list = list(set(id_list)) 
        if self.request.GET['data'] == "all":
            question_filter = queryset.filter().order_by('question')
        else:
            question_filter = queryset.filter().exclude(id__in=id_list).order_by('question')
        return question_filter
    
class DeleteQuestionsDetails(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        deleted_by, bkp_deleted_by = hitby_user(self,request) 
        data = request.data['data'] 
        for i in data:  
            # Soft delete Questions
            Questions.objects.filter(id=i).update(is_deleted=True,deleted_by=deleted_by,bkp_deleted_by=bkp_deleted_by,deleted_at=timezone.now()) 
        return Response(status=status.HTTP_200_OK)
    
class PutQuestionDetails(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk,format=None): 
        modified_by, bkp_modified_by = hitby_user(self,request) 
        instance = Questions.objects.get(id=pk) 
        serializer = QuestionsSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(modified_by=modified_by, bkp_modified_by=bkp_modified_by, modified_at=timezone.now())
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            print("ContactDetails serializer.errors", serializer.errors)
            return Response({"status": "error", "data": serializer.errors},)
        
class AddQuizDetails(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:   
            created_by, bkp_created_by = hitby_user(self,request)   
            serializer = QuizSerializer(data=request.data)
            if serializer.is_valid():
                quiz_instance = serializer.save(created_by=created_by,bkp_created_by=bkp_created_by, created_at=timezone.now()) 
                # total_time
                questions = quiz_instance.question.all()  
                total_seconds = 0
                for q in questions:
                    if q.time:
                        total_seconds += q.time.hour * 3600 + q.time.minute * 60 + q.time.second
                h = total_seconds // 3600
                m = (total_seconds % 3600) // 60
                s = total_seconds % 60
                quiz_instance.total_time = time(h, m, s)
                quiz_instance.save()  # Final save – total_time  
                return Response({"message": "Quiz added successfully!","data": serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": "Something went wrong!","details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetQuizDetails(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.select_related('user','created_by','modified_by','deleted_by').filter(is_deleted=False).order_by('-id')
    serializer_class = QuizSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['quiz_name', 'quiz_date', 'age_grup']
 
    def get_queryset(self):
        queryset = self.queryset.filter()
        return queryset
    
class GetQuizTransfer(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        quiz_id = request.GET['quiz_id']
        quiz_question = Quiz.objects.filter(id=quiz_id).values('question','question__question')
        return Response({'quiz_question': quiz_question})
    
class PutQuizDetails(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk,format=None): 
        modified_by, bkp_modified_by = hitby_user(self,request) 
        instance = Quiz.objects.get(id=pk) 
        serializer = QuizSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            quiz_instance = serializer.save(modified_by=modified_by, bkp_modified_by=bkp_modified_by, modified_at=timezone.now())
            # total_time
            questions = quiz_instance.question.all()  
            total_seconds = 0
            for q in questions:
                if q.time:
                    total_seconds += q.time.hour * 3600 + q.time.minute * 60 + q.time.second
            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            s = total_seconds % 60
            quiz_instance.total_time = time(h, m, s)
            quiz_instance.save()  # Final save – total_time
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            print("Quiz serializer.errors", serializer.errors)
            return Response({"status": "error", "data": serializer.errors},)
        
class DeleteQuizDetails(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        deleted_by, bkp_deleted_by = hitby_user(self,request) 
        data = request.data['data'] 
        for i in data:   
            Quiz.objects.filter(id=i).update(is_deleted=True,deleted_by=deleted_by,bkp_deleted_by=bkp_deleted_by,deleted_at=timezone.now()) 
        return Response(status=status.HTTP_200_OK)



class ShowBookingCreateAPI(APIView):
    def post(self, request):
        try:
            serializer = BookingShowSerializer(data=request.data)
            print("Requested",request.data)
            if serializer.is_valid():
                print("SSSSSSSSSSSSS")
                booking = serializer.save()  # Save the booking

                # ---------------------------------------
                # Prepare email content
                # ---------------------------------------
                user_email = request.data.get('email',None)  # who booked
                other_email = "mohitetechcube@gmail.com"             # another recipient
                recipient_list = [user_email, other_email]      # multiple recipients

                context = {
                    "booking": booking,
                    "recipient_name":request.data.get('name'),  # optional, use username
                    "support_email": "support@yourdomain.com",
                }

                html_message = render_to_string("show_booking.html", context)
                plain_message = strip_tags(html_message)

                # ---------------------------------------
                # Send email using send_mail
                # ---------------------------------------
                
                send_mail(
                    subject="Booking Confirmation",
                    message=plain_message,  # Plain text
                    from_email=os.environ.get("EMAIL_HOST_USER", "noreply@yourdomain.com"),
                    recipient_list=recipient_list,
                    fail_silently=False,
                    html_message=html_message,  # HTML content
                )


                # ---------------------------------------

                return Response(
                    {
                        "success": True,
                        "message": "Booking created successfully and emails sent",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            print("Serialiser Error",serializer.errors)
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            print("Exception Error",e)
            return Response(
                {"success": False, "error": f"Something went wrong: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
            
            
class ShowBookingListAPI(ListAPIView):
    permission_classes=[IsAdminUser]
    queryset = BookingShow.objects.all()
    serializer_class = BookingShowSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            return Response(
                {
                    "success": True,
                    "message": "Bookings fetched successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": f"Something went wrong: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
            
            
            
            
            # ------------------contactus--------------

            
class ContactusCreateAPI(APIView):
    def post(self, request):
        try:
            serializer = ContactUsSerializer(data=request.data)
            print("Requested",request.data)
            if serializer.is_valid():
                print("SSSSSSSSSSSSS")
                booking = serializer.save()  # Save the booking

                # ---------------------------------------
                # Prepare HTML and plain text email
                # ---------------------------------------
                context = {"booking": serializer.data}  # single booking info
                html_content = render_to_string(
                    "contactus.html", context
                )
                text_content = strip_tags(html_content)

                # ---------------------------------------
                # Multiple recipients
                # ---------------------------------------
                recipient_emails = [
                    serializer.data.get("email"),      # email of person who booked
                    "mohitetechcube@gmail.com",                 # another recipient
                ]

                email = EmailMultiAlternatives(
                    subject="Contact Us",
                    body=text_content,
                    from_email="noreply@yourdomain.com",
                    to=recipient_emails,   # send to all in list
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

                # ---------------------------------------

                return Response(
                    {
                        "success": True,
                        "message": "Your form is Submitted Successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            print("Serialiser Error",serializer.errors)
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            print("Exception Error",e)
            return Response(
                {"success": False, "error": f"Something went wrong: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
            
            
class ContactUsListAPI(ListAPIView):
    permission_classes=[IsAdminUser]
    queryset = Contactus.objects.all()
    serializer_class = ContactUsSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            return Response(
                {
                    "success": True,
                    "message": "Bookings fetched successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": f"Something went wrong: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )            
