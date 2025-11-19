from django.contrib import admin
from cards.models import *
from import_export.admin import ImportExportModelAdmin

class ContactDetailsAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display =[
        "user",
        "name", 
        "email", 
        "phone_number", 
        "company_name", 
        "designation", 
        "fax_no", 
        "street", 
        "city", 
        "zip_code", 
        "country", 
        "website", 
    ]
admin.site.register(ContactDetails,ContactDetailsAdmin)  
