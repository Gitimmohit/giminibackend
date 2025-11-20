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
from datetime import timedelta
from django.utils import timezone
from .mypaginations import MyPageNumberPagination
from django.db.models import F
# from core.common import get_financial_year, get_fy_month_year
from django.http import JsonResponse
from .models import * 
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
import io
from django.views.generic.base import RedirectView
from django.shortcuts import get_object_or_404

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
