from django.urls import path, include
from .views import *
urlpatterns = [
    path('signup/', SendOTPAPIView.as_view()),
    path('verify_otp/', VerifyOTPAPIView.as_view()),
    path('authentication/', GetLoginToken.as_view()),
    path('add_login_details/', Add_LoginDetail.as_view()),
    path('logout_user_details/', LogoutView.as_view()),
    path('change_pass/', ResetPassword.as_view()),
    path('check_username/',CheckUsername.as_view()),
    path('check_useremail/',CheckUserEmail.as_view()),
    path('check_userphone/',CheckUserPhone.as_view()),
    # for update the redux at the same time 
    path('get_user_info/',GetUserInfo.as_view()),
    path('get_user_details/',GetUserDetails.as_view()),
    path('put_user_details/<int:pk>',PutUserDetails.as_view()),
    path('delete_user_details/', DeleteUserDetails.as_view()),

    
    path('check-duplicate-email/',CheckDuplicateEmail.as_view()),
]