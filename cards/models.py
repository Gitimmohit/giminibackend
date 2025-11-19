from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from ems.models import *


  
def qr_logo_path(instance, filename):
    date = datetime.date.today().strftime('%Y-%m-%d')
    today = date.split('-')
    current_year = int(today[0])
    c_month = datetime.datetime.now().month
    current_month = '{:02d}'.format(c_month)
    if int(today[1]) < int("04"):
        fy = str(current_year-1) + "-" + str(current_year)
    else:
        fy = str(current_year) + "-" + str(current_year+1)
    return f"{fy}/{current_month}/fixed/contactdetails/qr_logo/{filename}"

class ContactDetails(models.Model): 
    user = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    salutation = models.CharField(max_length=5 , blank=True , null=True , verbose_name='Salutation')
    name = models.CharField(max_length=30,blank=True, null=True,verbose_name='Name') 
    qr_type = models.CharField(max_length=30,blank=True, null=True,verbose_name='QR Type') 
    qr_color = models.CharField(max_length=20,blank=True, null=True,verbose_name='QR Color') 
    qr_logo = models.FileField(upload_to=qr_logo_path,null=True,blank=True,)  
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
 