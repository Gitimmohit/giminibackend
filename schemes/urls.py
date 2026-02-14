from django.urls import path
from .views import * 

urlpatterns = [ 
    path('add_investment_scheme/', AddInvestmentScheme.as_view()), 
    path('put_investment_scheme/<int:pk>', PutInvestmentScheme.as_view()),
    path('put_approved_investment_scheme/<int:pk>', PutApprovedInvestmentScheme.as_view()),
    path('get_investment_scheme/', GetInvestmentScheme.as_view()), 
    path('delete_investment_scheme/', DeleteInvestmentScheme.as_view()),

    path('add_investment/', AddInvestment.as_view()), 
    path('get_investment/', GetInvestment.as_view()), 
    path('get_levelwise_referralearning/', GetLevelWiseReferralEarningView.as_view()), 
]