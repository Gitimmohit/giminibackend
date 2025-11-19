from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from ems.models import *


  
def study_material(instance, filename):
    date = datetime.date.today().strftime('%Y-%m-%d')
    today = date.split('-')
    current_year = int(today[0])
    c_month = datetime.datetime.now().month
    current_month = '{:02d}'.format(c_month)
    if int(today[1]) < int("04"):
        fy = str(current_year-1) + "-" + str(current_year)
    else:
        fy = str(current_year) + "-" + str(current_year+1)
    return f"{fy}/{current_month}/fixed/contactdetails/study_material/{filename}"

class ContactDetails(models.Model): 
    user = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    salutation = models.CharField(max_length=5 , blank=True , null=True , verbose_name='Salutation')
    name = models.CharField(max_length=30,blank=True, null=True,verbose_name='Name') 
    qr_type = models.CharField(max_length=30,blank=True, null=True,verbose_name='QR Type') 
    qr_color = models.CharField(max_length=20,blank=True, null=True,verbose_name='QR Color') 
    study_material = models.FileField(upload_to=study_material,null=True,blank=True,)  
    no_of_times_scan =models.BigIntegerField(default=0,verbose_name="No Of Times Scan ContactDetails",) 
    no_of_times_download =models.BigIntegerField(default=0,verbose_name="No Of Times Download ContactDetails",)
    email = models.EmailField(null=True, blank=True,verbose_name='Email')
    phone_number = models.BigIntegerField(blank=True, null=True,verbose_name='Phone Number') 
    company_name = models.CharField(max_length=50,null=True,blank=True,verbose_name='Company Name')  
    designation = models.CharField(max_length=50,null=True,blank=True,verbose_name='Designation')  
    fax_no = models.CharField(max_length=50,null=True,blank=True,verbose_name='Fax No')  
    street = models.CharField(max_length=150,blank=True,null=True,verbose_name='Street') 
    city = models.CharField(max_length=50,  blank=True, null=True,verbose_name="City Name")
    zip_code = models.PositiveBigIntegerField( blank=True, null=True,verbose_name="Zip Code",)
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name="Country Name",)
    website = models.URLField(max_length=50, null=True,blank=True, verbose_name="Website Address")
    valid_upto = models.DateTimeField(null=True,blank=True,verbose_name='Valid Upto')
    file_name = models.CharField( max_length=30,null=True , blank=True , verbose_name="File Name")
    is_deleted   = models.BooleanField(default=False,verbose_name="Is Deleted",null=True,blank=True,)
    deleted_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True, related_name="contactdetails_deletor")
    deleted_at   = models.DateTimeField(null=True)
    created_at   = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Created At')
    modified_at  = models.DateTimeField(null=True,blank=True,verbose_name='Modified At')
    created_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='ContactDetails Created By', related_name="contactdetails_creater")
    modified_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='ContactDetails Modified By', related_name="contactdetails_modifier")
    bkp_deleted_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Deletor")
    bkp_created_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Created By")
    bkp_modified_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Modified By")


    class Meta:
        verbose_name='ContactDetails' 

    def __str__(self):
         return self.name
 

# for the quiz
class Questions(models.Model): 
    user            = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    question        = models.TextField(blank=True , null=True , verbose_name='Salutation')
    answare         = models.TextField(blank=True , null=True , verbose_name='answare')
    time            = models.TimeField(blank=True , null=True , verbose_name='time')
    age_grup        = models.TimeField(blank=True , null=True , verbose_name='age_group')
    
    option1         = models.TextField(blank=True , null=True , verbose_name='option1')
    option2         = models.TextField(blank=True , null=True , verbose_name='option2')
    option3         = models.TextField(blank=True , null=True , verbose_name='option3')
    option4         = models.TextField(blank=True , null=True , verbose_name='option4')
   
    is_deleted      = models.BooleanField(default=False,verbose_name="Is Deleted",null=True,blank=True,)
    deleted_by      = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True, related_name="contactdetails_deletor")
    deleted_at      = models.DateTimeField(null=True)
    created_at      = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Created At')
    modified_at     = models.DateTimeField(null=True,blank=True,verbose_name='Modified At')
    created_by      = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='ContactDetails Created By', related_name="contactdetails_creater")
    modified_by     = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='ContactDetails Modified By', related_name="contactdetails_modifier")
    bkp_deleted_by  = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Deletor")
    bkp_created_by  = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Created By")
    bkp_modified_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Modified By")

 

class QuizSubmission(models.Model): 
    user = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    question = models.ForeignKey('cards.Questions', on_delete=models.SET_NULL, null=True, blank=True, related_name='quiz_question', verbose_name="question")
    submit_time = models.TimeField(blank=True , null=True , verbose_name='submit_time')

    is_deleted   = models.BooleanField(default=False,verbose_name="Is Deleted",null=True,blank=True,)
    deleted_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True, related_name="contactdetails_deletor")
    deleted_at   = models.DateTimeField(null=True)
    created_at   = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Created At')
    modified_at  = models.DateTimeField(null=True,blank=True,verbose_name='Modified At')
    created_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='ContactDetails Created By', related_name="contactdetails_creater")
    modified_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='ContactDetails Modified By', related_name="contactdetails_modifier")
    bkp_deleted_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Deletor")
    bkp_created_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Created By")
    bkp_modified_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Modified By")


 
class Quiz(models.Model): 
    user = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    total_time = models.TimeField(blank=True , null=True , verbose_name='total_time')
    question = models.ForeignKey('cards.Questions', on_delete=models.SET_NULL, null=True, blank=True, related_name='quiz_question', verbose_name="question")

    is_deleted   = models.BooleanField(default=False,verbose_name="Is Deleted",null=True,blank=True,)
    deleted_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True, related_name="contactdetails_deletor")
    deleted_at   = models.DateTimeField(null=True)
    created_at   = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Created At')
    modified_at  = models.DateTimeField(null=True,blank=True,verbose_name='Modified At')
    created_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='ContactDetails Created By', related_name="contactdetails_creater")
    modified_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='ContactDetails Modified By', related_name="contactdetails_modifier")
    bkp_deleted_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Deletor")
    bkp_created_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Created By")
    bkp_modified_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Modified By")

class Tranactions(models.Model): 
    user = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    request_type = models.TextField(blank=True , null=True , verbose_name='request_type')
    current_status = models.TextField(default="PENDING",blank=True , null=True , verbose_name='current_status')
    request_time = models.DateTimeField(blank=True , null=True , verbose_name='request_time')

    is_deleted   = models.BooleanField(default=False,verbose_name="Is Deleted",null=True,blank=True,)
    deleted_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True, related_name="contactdetails_deletor")
    deleted_at   = models.DateTimeField(null=True)
    created_at   = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Created At')
    modified_at  = models.DateTimeField(null=True,blank=True,verbose_name='Modified At')
    created_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='ContactDetails Created By', related_name="contactdetails_creater")
    modified_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='ContactDetails Modified By', related_name="contactdetails_modifier")
    bkp_deleted_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Deletor")
    bkp_created_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Created By")
    bkp_modified_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Modified By")


 