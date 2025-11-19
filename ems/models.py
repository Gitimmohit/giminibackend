from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    usertype            = models.CharField(default = "STUDENT",max_length=50, verbose_name="User Type", blank=True, null=True)
    username            = models.CharField(max_length=30) 
    email               = models.EmailField(null=True, blank=True, unique=True)
    mobilenumber        = models.CharField(max_length=12, blank=True, null=True) 
    password            = models.CharField(max_length=100, null=False)
    title               = models.CharField(max_length=8,blank=True,null=True) 
    firstname           = models.CharField(max_length=500, verbose_name="FIrst Name", blank=True, null=True)
    middlename          = models.CharField(max_length=50,null=True,blank=True,verbose_name='Middle Name')  
    lastname            = models.CharField(max_length=500, verbose_name="Last Name", blank=True, null=True)
    school_name         = models.CharField(max_length=500, verbose_name="School Name", blank=True, null=True)
    student_class       = models.CharField(max_length=500, verbose_name="Student Name", blank=True, null=True)
    dob                 = models.DateField(editable=False,default=timezone.now,verbose_name='Date of birth')
    password_changed_by = models.CharField(max_length=20,null=True,blank=True,verbose_name='Password Changed By')
    password_changed    = models.BooleanField(default=False)
    password_changed_date = models.DateTimeField(blank=True, null=True)
    is_superuser        = models.BooleanField(default=False)
    is_staff            = models.BooleanField(default=False)
    is_active           = models.BooleanField(default=True) 
    is_payment          = models.BooleanField(default=False) 
    is_first_quiz       = models.BooleanField(default=False) 
    is_first_show       = models.BooleanField(default=False) 
    last_password_reset_date     = models.DateField(auto_now_add=True,blank=True,null=True,verbose_name='Last Password Reset Date')
    next_password_reset_date     = models.DateField(auto_now_add=True,blank=True,null=True,verbose_name='Next Password Reset Date')

    is_deleted          = models.BooleanField(default=False,verbose_name="Is Deleted")
    deleted_by          = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, related_name="ems_deletor")
    deleted_at          = models.DateTimeField(null=True)
    created_at          = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Created At')
    modified_at         = models.DateTimeField(null=True,verbose_name='Modified At')
    created_by          = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,verbose_name='Created By', related_name="customuser_creater")
    modified_by         = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,verbose_name='Modified By', related_name="customuser_modifier")
    bkp_deleted_by      = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Deletor")
    bkp_created_by      = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Created By")
    bkp_modified_by     = models.CharField(max_length=100, null=True, blank=True, verbose_name="Backup Modified By")


    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username
    
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
