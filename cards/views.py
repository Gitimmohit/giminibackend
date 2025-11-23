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
from django.db.models import Count, Q, Min, F,Max

from decimal import Decimal


 
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
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "error", "data": serializer.errors})


class AddTranaction(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        print("AddContactDetails REQUEST DATA==", request.data) 
        data=request.data
        user = request.data.get('user',None)        
        serializer = TransactionsSerializer(data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save(
                created_by_id=request.user.id,
                bkp_created_by=request.user.fullname.upper() if request.user.fullname else None, 
                created_at=timezone.now(),
                request_time = timezone.now(),
                )
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
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

class GetAllTransactions(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Transactions.objects.select_related('user','created_by','modified_by','deleted_by').filter(is_deleted=False).order_by('-id')
    serializer_class = TransactionsSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['user__fullname', 'request_type', 'current_status', 'request_time', 'transactionId','transaction_amt']
 
    def get_queryset(self):
        filter_type = self.request.query_params.get('filter_type',None)

        filters = {}
        if filter_type == "USER":
            filters['user_id'] = self.request.user.id

        queryset = self.queryset.filter(**filters)
        return queryset



class PutTransactionDetails(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk, format=None):
        modified_by, bkp_modified_by = hitby_user(self, request)

        transaction_amt = request.data.get('transaction_amt', None)
        current_status = request.data.get('current_status')
        is_transaction_complete = False
        if current_status  != "PENDING":
            is_transaction_complete = True

        transaction_amt = Decimal(transaction_amt) if transaction_amt else Decimal("0")

        current_instance = Transactions.objects.get(id=pk)
        is_credit = current_instance.is_transaction_complete

        serializer = TransactionsSerializer(current_instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save(
                modified_by=modified_by, 
                bkp_modified_by=bkp_modified_by, 
                modified_at=timezone.now(),
                is_transaction_complete = is_transaction_complete,
            )
            print("is_credit---",is_credit,current_status)
            # Update wallet after approval
            if request.data.get('request_type') == "CR" and request.data.get('current_status') == "APPROVED" and not is_credit:
                wallet = Wallet.objects.filter(user=current_instance.user).first()

                if wallet:
                    wallet.current_wallet_amount = wallet.current_wallet_amount + transaction_amt
                    wallet.save()
                else:
                    Wallet.objects.create(
                        user=current_instance.user,
                        current_wallet_amount=transaction_amt,
                        created_at=timezone.now(),
                    )
            if request.data.get('request_type') == "DR" and request.data.get('current_status') == "APPROVED" and not is_credit:
                wallet = Wallet.objects.filter(user=current_instance.user).first()

                if wallet:
                    wallet.current_wallet_amount = wallet.current_wallet_amount - transaction_amt
                    wallet.save()
                else:
                    return Response({"status": "error", "msg": "No Amount Found"},status=status.HTTP_200_OK)

            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response({"status": "error", "data": serializer.errors})



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
    
class GetQuizPlayData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        quiz_id = request.GET.get('quiz_id')

        if not quiz_id:
            return Response({"success": False,"message": "quiz_id is required in query params"}, status=400)

        # Quiz exist karta hai ya nahi + soft delete check
        quiz = get_object_or_404(Quiz, id=quiz_id,)

        # Saare questions jo is quiz mein hain aur deleted nahi hain
        questions_qs = quiz.question.filter(is_deleted=False).order_by('id')

        # Final data jo frontend ko exactly chahiye
        quiz_data = []
        for q in questions_qs:
            time_delta = q.time
            time_in_seconds = time_delta.hour * 3600 + time_delta.minute * 60 + time_delta.second if time_delta else 30
            quiz_data.append({
                "id": q.id,
                "quiz_id": quiz_id,
                "question": q.question or "",
                "time":time_in_seconds,
                "options": [
                    {"id": "A", "text": q.option1 or ""},
                    {"id": "B", "text": q.option2 or ""},
                    {"id": "C", "text": q.option3 or ""},
                    {"id": "D", "text": q.option4 or ""},
                ],
            })

        return Response({"success": True,"quiz_name": quiz.quiz_name,"total_time": quiz.total_time.strftime("%H:%M:%S") if quiz.total_time else None,"quiz_data": quiz_data})
    
# class GetQuizUpcomingData(ListAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = Quiz.objects.select_related('user','created_by','modified_by','deleted_by').filter(is_deleted=False).order_by('-quiz_name')
#     serializer_class = QuizSerializer
#     pagination_class = MyPageNumberPagination
#     filter_backends = [SearchFilter]
#     search_fields = ['quiz_name', 'quiz_date', 'age_grup']
 
#     def get_queryset(self):
#         now = timezone.now() 
#         after_24_hours = now + timedelta(hours=24)
#         queryset = self.queryset.filter(quiz_date__gt=after_24_hours).order_by('-quiz_name')
#         return queryset

class GetQuizUpcomingData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        after_24_hours = now + timedelta(hours=24)
        quizzes = Quiz.objects.filter(is_deleted=False,quiz_date__gt=after_24_hours).select_related('user', 'created_by', 'modified_by', 'deleted_by').order_by('-quiz_date')
        serializer = QuizSerializer(quizzes, many=True)
        return Response({"success": True,"count": quizzes.count(),"upcoming_quizzes": serializer.data})
     
class AddQuizSubmissionDetails(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request): 
        try:
            created_by, bkp_created_by = hitby_user(self, request)
            serializer = QuizSubmissionSerializer(data=request.data)
            if serializer.is_valid():
                submission = serializer.save(created_by=created_by,bkp_created_by=bkp_created_by,created_at=timezone.now(),submit_time=timezone.now())
                quiz_id = request.data.get('quiz')  
                if quiz_id:
                    Quiz.objects.filter(id=quiz_id, is_completed=False).update(is_completed=True)
                return Response({"success": True,"message": "Answer saved successfully!"}, status=201)
            else:
                return Response(serializer.errors, status=400)

        except Exception as e:
            return Response({"success": False, "error": "Something went wrong!","details": str(e)}, status=500)
        
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
    

class QuizReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        quiz_id = request.GET.get('quiz_id')
        if not quiz_id:
            return Response({"success": False, "message": "quiz_id is required"}, status=400)
        quiz = Quiz.objects.filter(id=quiz_id).first()
        if not quiz:
            return Response({"success": False, "message": "Quiz not found"}, status=404)
        
        total_questions = quiz.question.count()
        submissions = QuizSubmission.objects.filter(quiz_id=quiz_id, is_deleted=False)

        if not submissions.exists():
            return Response({"success": True,"quiz_id": quiz_id,"quiz_name": quiz.quiz_name,"total_participants": 0,"leaderboard": [],"winner": None})

        users = submissions.values(
            'created_by__id',
            'created_by__fullname',
            'created_by__email'
        ).annotate(
            total_attempted=Count('id'),
            correct_answers=Count('id', filter=Q(is_answered=F('question__answare'))),
            wrong_answers=Count('id', filter=~Q(is_answered=F('question__answare'))),
            score=Count('id', filter=Q(is_answered=F('question__answare'))),
            first_submit=Min('submit_time'),
            last_submit=Max('submit_time')
        ) 

        leaderboard = []

        for u in users:
            user_id = u['created_by__id']
            username = u['created_by__fullname'] or u['created_by__email']
            email = u['created_by__email']

            start = u['first_submit']
            end = u['last_submit']

            # ---- FIX: TIMEFIELD DIFFERENCE WITH MICROSECONDS ----
            if start and end:
                start_seconds = start.hour * 3600 + start.minute * 60 + start.second + (start.microsecond / 1_000_000)
                end_seconds = end.hour * 3600 + end.minute * 60 + end.second + (end.microsecond / 1_000_000)

                total_seconds = abs(end_seconds - start_seconds)

                diff_int = int(total_seconds)
                h = diff_int // 3600
                m = (diff_int % 3600) // 60
                s = diff_int % 60

                time_taken = f"{h:02}:{m:02}:{s:02}"
            else:
                total_seconds = None
                time_taken = None
            # -----------------------------------------------------

            leaderboard.append({
                "user_id": user_id,
                "username": username,
                "email": email,
                "total_questions": total_questions,
                "total_questions_attempted": u['total_attempted'],
                "correct_answers": u['correct_answers'],
                "wrong_answers": u['wrong_answers'],
                "score": u['score'],
                "time_taken": time_taken,
                "raw_time": total_seconds
            })

        # SORT: Score desc, time asc
        def sort_key(item):
            t = item["raw_time"]
            if t is None:
                t = float('inf')
            return (-item["score"], t)

        leaderboard = sorted(leaderboard, key=sort_key)

        # WINNER
        winner = leaderboard[0] if leaderboard else None
        # ADD WINNER FLAG TO LEADERBOARD
        for item in leaderboard:
            item["is_winner"] = (winner and item["user_id"] == winner["user_id"])

        return Response({
            "success": True,
            "quiz_id": quiz.id,
            "quiz_name": quiz.quiz_name,
            "total_participants": len(leaderboard),
            "leaderboard": leaderboard,
            "winner": winner
        }, status=200)
