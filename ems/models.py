from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import CustomUserManager

def document_file_path(instance, filename):  
    user_alias = instance.email  
    return f"{user_alias}/documents/{filename}"
class CustomUser(AbstractBaseUser, PermissionsMixin):
    usertype            = models.CharField(default = "STUDENT",max_length=50, verbose_name="User Type", blank=True, null=True)
    first_payment       = models.CharField(default = "NOT DONE",max_length=50, verbose_name="First Payment", blank=True, null=True)
    email               = models.EmailField(null=True, blank=True, unique=True)
    mobilenumber        = models.CharField(max_length=12, blank=True, null=True) 
    referalcode         = models.CharField(unique=True,max_length=12, blank=True, null=True) 
    refered_code        = models.CharField(max_length=12, blank=True, null=True) 
    reffered_by         = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, related_name="customuser_reffered_by")
    reffered_amt_credit = models.BooleanField(default=False)
    password            = models.CharField(max_length=100, null=False)
    title               = models.CharField(max_length=8,blank=True,null=True) 
    fullname            = models.CharField(max_length=500, verbose_name="Full Name", blank=True, null=True)
    school_name         = models.CharField(max_length=500, verbose_name="School Name", blank=True, null=True)
    student_class       = models.CharField(max_length=500, verbose_name="Student Name", blank=True, null=True)
    dob                 = models.DateField(verbose_name='Date of birth',blank=True,null=True)
    password_changed_by = models.CharField(max_length=20,null=True,blank=True,verbose_name='Password Changed By')
    password_changed    = models.BooleanField(default=False)
    password_changed_date = models.DateTimeField(blank=True, null=True)
    is_superuser        = models.BooleanField(default=False)
    is_approved         = models.BooleanField(default=False)
    mail_sended         = models.BooleanField(default=False)
    first_login         = models.BooleanField(default=False)
    is_active           = models.BooleanField(default=True) 
    is_payment          = models.BooleanField(default=False) 
    is_first_quiz       = models.BooleanField(default=False) 
    is_first_show       = models.BooleanField(default=False) 
    kyc_status          = models.CharField(default="NOT SUBMITTED",verbose_name='Kyc Status')
    kyc_submit_time     = models.DateTimeField(blank=True , null=True , verbose_name='Kyc Submit Time')
    kyc_reject_reason   = models.TextField(max_length=100,blank=True , null=True , verbose_name='Kyc  Reject Reason')
    document_type       = models.CharField(max_length=100,blank=True , null=True , verbose_name='Documnet Type')
    document_number     = models.CharField(max_length=100,blank=True , null=True , verbose_name='Documnet Number')
    document_file       = models.FileField(upload_to=document_file_path, default="",blank=True , null=True )
    last_password_reset_date     = models.DateField(auto_now_add=True,blank=True,null=True,verbose_name='Last Password Reset Date')
    next_password_reset_date     = models.DateField(auto_now_add=True,blank=True,null=True,verbose_name='Next Password Reset Date')

    is_deleted          = models.BooleanField(default=False,verbose_name="Is Deleted")
    deleted_by          = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, related_name="ems_deletor")
    deleted_at          = models.DateTimeField(null=True)
    created_at          = models.DateTimeField(editable=False,default=timezone.now,verbose_name='CustomUser_Created At')
    modified_at         = models.DateTimeField(null=True,verbose_name='Modified At')
    created_by          = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,verbose_name='CustomUser_Created By', related_name="customuser_creater")
    modified_by         = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,verbose_name='CustomUser_Modified By', related_name="customuser_modifier")
    bkp_deleted_by      = models.CharField(max_length=100, null=True, blank=True, verbose_name="CustomUser_Backup Deletor")
    bkp_created_by      = models.CharField(max_length=100, null=True, blank=True, verbose_name="CustomUser_Backup Created By")
    bkp_modified_by     = models.CharField(max_length=100, null=True, blank=True, verbose_name="CustomUser_Backup Modified By")
    pincode             = models.CharField(max_length=6, null=True, blank=True, verbose_name="CustomUser Pincode")
    address             = models.TextField(null=True, blank=True, verbose_name="CustomUser Address")
    is_demo_done        = models.BooleanField(null=True, default=False,blank=True, verbose_name="Demo Quiz")


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
class OTPRecord(models.Model):
    email   = models.EmailField(null=True, blank=True, )
    token   = models.UUIDField(unique=True)
    otp     = models.CharField(max_length=6)
    
class LoginDetail(models.Model):  
    user        = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='user_login_details')
    user_ip     = models.CharField(max_length=100,null=True,blank=True,verbose_name='User Ip')
    user_lat    = models.CharField(max_length=100,null=True,blank=True,verbose_name='User Lat')
    user_long   = models.CharField(max_length=100,null=True,blank=True,verbose_name='User Long')
    is_mobile   = models.BooleanField(null=True,blank=True,verbose_name='is_mobile')
    os          = models.CharField(max_length=100,null=True,blank=True,verbose_name='os')
    login_time  = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Login Time')
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name='Login Time')

    def __str__(self):
        return self.user_ip
class BankDetails(models.Model): 
    user         = models.ForeignKey(CustomUser, blank=True, on_delete=models.SET_NULL, null=True,related_name='bank_details_user')
    ifsc_code    = models.CharField(max_length=500, verbose_name="IFSC Code", blank=True, null=True)
    bank_name    = models.CharField(max_length=500, verbose_name="Bank Name", blank=True, null=True)
    bank_branch_name = models.CharField(max_length=500, verbose_name="Bank Branch Name", blank=True, null=True)
    bank_branch_address = models.CharField(max_length=500, verbose_name="Bank Branch Address", blank=True, null=True)
    acc_type     = models.CharField(max_length=500, verbose_name="Account Type", blank=True, null=True)
    account_no   = models.CharField(max_length=500, verbose_name="Account Number", blank=True, null=True)
    confirm_account_no = models.CharField(max_length=500, verbose_name="Confirm Account Number", blank=True, null=True)
    account_holder_name= models.CharField(max_length=500, verbose_name="Account Holder Name", blank=True, null=True)
     
    created_at   = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Created At')
    created_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='BankDetails Created By', related_name="bank_details_creater")
    bkp_created_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="BankDetails Created By")
