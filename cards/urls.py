from django.urls import path, include
from .views import * 

urlpatterns = [ 
    path('add_contact_details/', AddContactDetails.as_view()),
    path('get_contact_details/', GetContactDetails.as_view()),
    path('put_contact_details/<int:pk>', PutContactDetails.as_view()),
  


]