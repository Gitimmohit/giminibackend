from django.urls import path, include
from .views import * 

urlpatterns = [ 
    path('add_contact_details/', AddContactDetails.as_view()),
    path('get_contact_details/', GetContactDetails.as_view()),
    path('put_contact_details/<int:pk>', PutContactDetails.as_view()),
    
    # for first payment
    path('first_payment_receipt/', AddPayment.as_view()),
    path('add_tranaction/', AddTranaction.as_view()), 
    path('getfirst_payment_receipt/', FirstPayment.as_view()),
    path('transaction-request/', GetAllTransactions.as_view()),
    path('put_tranaction/<int:pk>', PutTransactionDetails.as_view()),
    # for dashboard --
    path('getwallet-data/', GetWalletDetails.as_view()),

    path('add_question_details/', AddQuestionDetails.as_view()), 
    path('put_question_details/<int:pk>', PutQuestionDetails.as_view()),
    path('get_question_details/', GetQuestionsDetails.as_view()),
    path('get_question_transfer/', GetQuestionsTransfer.as_view()),
    path('delete_question_details/', DeleteQuestionsDetails.as_view()),

    path('add_quiz_details/', AddQuizDetails.as_view()), 
    path('put_quiz_details/<int:pk>', PutQuizDetails.as_view()),
    path('get_quiz_details/', GetQuizDetails.as_view()), 
    path('get_quiz_transfer/', GetQuizTransfer.as_view()), 
    path('delete_quiz_details/', DeleteQuizDetails.as_view()),
    path('get_quiz_play_data/', GetQuizPlayData.as_view()),
    path('get_upcoming_quiz_data/', GetQuizUpcomingData.as_view()),
    path('add_quiz_submission_details/', AddQuizSubmissionDetails.as_view()),
    path('quiz_report_view/', QuizReportView.as_view()),
    path('bulk_create_qestions_details/', BulkCreateBankStatement.as_view()),

]