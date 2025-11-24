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
    created_at   = models.DateTimeField(editable=False,default=timezone.now,verbose_name='ContactDetails_Created At')
    modified_at  = models.DateTimeField(null=True,blank=True,verbose_name='ContactDetails_Modified At')
    created_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='ContactDetails Created By', related_name="contactdetails_creater")
    modified_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='ContactDetails Modified By', related_name="contactdetails_modifier")
    bkp_deleted_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="ContactDetails_Backup Deletor")
    bkp_created_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="ContactDetails_Backup Created By")
    bkp_modified_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="ContactDetails_Backup Modified By")


    class Meta:
        verbose_name='ContactDetails' 

    def __str__(self):
         return self.name
 

# for the quiz
class Questions(models.Model): 
    ANSWER_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    user            = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    question        = models.TextField(blank=True , null=True , verbose_name='Question')
    answer         = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    time            = models.TimeField(blank=True , null=True , verbose_name='time')
    age_grup        = models.CharField(max_length=2,blank=True , null=True , verbose_name='age_group')
    
    option1         = models.TextField(blank=True , null=True , verbose_name='option1')
    option2         = models.TextField(blank=True , null=True , verbose_name='option2')
    option3         = models.TextField(blank=True , null=True , verbose_name='option3')
    option4         = models.TextField(blank=True , null=True , verbose_name='option4')
   
    is_deleted      = models.BooleanField(default=False,verbose_name="Is Deleted",null=True,blank=True,)
    deleted_by      = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True, related_name="Questions_deletor")
    deleted_at      = models.DateTimeField(null=True)
    created_at      = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Questions_Created At')
    modified_at     = models.DateTimeField(null=True,blank=True,verbose_name='Questions_Modified At')
    created_by      = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='Question Created By', related_name="Questions_creater")
    modified_by     = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='Questions Modified By', related_name="Questions_modifier")
    bkp_deleted_by  = models.CharField(max_length=100, null=True, blank=True, verbose_name="Questions Deletor")
    bkp_created_by  = models.CharField(max_length=100, null=True, blank=True, verbose_name="Questions Created By")
    bkp_modified_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Questions Modified By")

 

class QuizSubmission(models.Model): 
    user = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    question = models.ForeignKey('cards.Questions', on_delete=models.SET_NULL, null=True, blank=True, related_name='quiz_submission_question', verbose_name="question")
    quiz = models.ForeignKey('cards.Quiz', on_delete=models.SET_NULL, null=True, blank=True, related_name='quiz_submission_quiz', verbose_name="Quiz Id")
    submit_time = models.DateTimeField(blank=True , null=True , verbose_name='submit_time')
    ANSWER_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    is_answered=models.CharField(max_length=1, choices=ANSWER_CHOICES ,null=True,blank=True)
    is_deleted   = models.BooleanField(default=False,verbose_name="Is Deleted",null=True,blank=True,)
    deleted_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True, related_name="QuizSubmission_deletor")
    deleted_at   = models.DateTimeField(null=True)
    created_at   = models.DateTimeField(editable=False,default=timezone.now,verbose_name='QuizSubmission_Created At')
    modified_at  = models.DateTimeField(null=True,blank=True,verbose_name='QuizSubmission_Modified At')
    created_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='QuizSubmission Created By', related_name="QuizSubmission_creater")
    modified_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='QuizSubmission Modified By', related_name="QuizSubmission_modifier")
    bkp_deleted_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="QuizSubmission_Backup Deletor")
    bkp_created_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="QuizSubmission_Backup Created By")
    bkp_modified_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="QuizSubmission_Backup Modified By")


 
class Quiz(models.Model): 
    user         = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    total_time   = models.TimeField(blank=True , null=True , verbose_name='total_time')
    question     = models.ManyToManyField('cards.Questions', blank=True, related_name='quiz_question', verbose_name="question")
    quiz_name    = models.TextField(blank=True , null=True , verbose_name='Quiz Name')
    quiz_date    = models.DateTimeField(blank=True , null=True , verbose_name='Quiz Date Time')
    age_grup     = models.CharField(max_length=2,blank=True , null=True , verbose_name='age_group')
    prize_money  = models.TextField(blank=True , null=True ,verbose_name='Prize Money')
    entry_fee    = models.DecimalField(max_digits=11,decimal_places=2,default=0,verbose_name='Entry Fee')
    is_completed = models.BooleanField(default=False,verbose_name="Is Completed",null=True,blank=True,)
    
    is_deleted   = models.BooleanField(default=False,verbose_name="Is Deleted",null=True,blank=True,)
    deleted_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True, related_name="Quiz_deletor")
    deleted_at   = models.DateTimeField(null=True)
    created_at   = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Created At')
    modified_at  = models.DateTimeField(null=True,blank=True,verbose_name='Modified At')
    created_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='Quiz Created By', related_name="Quiz_creater")
    modified_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='Quiz Modified By', related_name="Quiz_modifier")
    bkp_deleted_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Quiz_Backup Deletor")
    bkp_created_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Quiz_Backup Created By")
    bkp_modified_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Quiz_Backup Modified By")

class QuizParticipant(models.Model): 
    user                = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    quiz_status         = models.CharField(default="PENDING",max_length=100,blank=True , null=True , verbose_name='Quiz Status',)
    quiz                = models.ForeignKey('cards.Quiz', on_delete=models.SET_NULL, null=True, blank=True, related_name='quizparticipant_quiz', verbose_name="Quiz Id")
    participating_date  = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Participating At')



class Transactions(models.Model): 
    user = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    request_type = models.CharField(max_length=100,blank=True , null=True , verbose_name='request_type')
    current_status = models.TextField(default="PENDING",blank=True , null=True , verbose_name='current_status')
    request_time = models.DateTimeField(blank=True , null=True , verbose_name='request_time')
    transactionId = models.CharField(max_length=100,blank=True , null=True , verbose_name='transactionId')
    transaction_amt = models.CharField(max_length=100,blank=True , null=True , verbose_name='transaction_amt')
    transaction_from = models.CharField(max_length=100,blank=True , null=True , verbose_name='transaction_from')

    is_first_transaction   = models.BooleanField(default=False,verbose_name="First Transaction",null=True,blank=True,)
    is_transaction_complete   = models.BooleanField(default=False,verbose_name="First Transaction",null=True,blank=True,)
    is_deleted   = models.BooleanField(default=False,verbose_name="Is Deleted",null=True,blank=True,)
    deleted_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True, related_name="Transactions_deletor")
    deleted_at   = models.DateTimeField(null=True)
    created_at   = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Created At')
    modified_at  = models.DateTimeField(null=True,blank=True,verbose_name='Modified At')
    created_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='Transactions Created By', related_name="Transactions_creater")
    modified_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='Transactions Modified By', related_name="Transactions_modifier")
    bkp_deleted_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Transaction_Backup Deletor")
    bkp_created_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Transaction_Backup Created By")
    bkp_modified_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Transaction_Backup Modified By")



class Wallet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name="wallets")
    earn_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    current_wallet_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - Wallet"

        
class BookingShow(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    mobile = models.CharField(max_length=20,null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    school = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=150,blank=True, null=True)
    students = models.CharField(blank=True, null=True)
    created_at=models.DateTimeField(null=True, blank=True, default=timezone.now)

    def __str__(self):
        return self.name or "Booking"


class Contactus(models.Model):
    name=models.CharField(max_length=100,blank=True, null=True)
    email=models.EmailField(blank=True, null=True)  
    inquiry_type =models.TextField(max_length=200,null=True, blank=True)
    subject=models.TextField(max_length=150, null=True, blank=True)
    message=models.TextField(max_length=150, null=True, blank=True)
    created_at=models.DateTimeField(null=True, blank=True, default=timezone.now)
