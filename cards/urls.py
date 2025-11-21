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
    path('put_question_details/<int:pk>', PutQuestionDetails.as_view()),
    path('get_question_details/', GetQuestionsDetails.as_view()),
    path('delete_question_details/', DeleteQuestionsDetails.as_view()),

    path('add_quiz_details/', AddQuizDetails.as_view()), 
    path('put_quiz_details/<int:pk>', PutQuizDetails.as_view()),
    path('get_quiz_details/', GetQuizDetails.as_view()), 
    path('get_quiz_question/', GetQuizQuestion.as_view()), 

]