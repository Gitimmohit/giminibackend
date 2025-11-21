from django.urls import path, include
from .views import * 

urlpatterns = [ 
    path('add_contact_details/', AddContactDetails.as_view()),
    path('get_contact_details/', GetContactDetails.as_view()),
    path('put_contact_details/<int:pk>', PutContactDetails.as_view()),
    
    # for first payment
    path('first_payment_receipt/', AddPayment.as_view()),
    path('getfirst_payment_receipt/', FirstPayment.as_view()),

    path('add_question_details/', AddQuestionDetails.as_view()), 
    path('get_question_details/', GetQuestionsDetails.as_view()),


]