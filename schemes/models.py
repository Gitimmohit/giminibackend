from django.db import models
from ems.models import *

class InvestmentScheme(models.Model):
    scheme_type = models.CharField(max_length=20)
    investment_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    return_amount = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    duration_months = models.PositiveIntegerField(null=True,blank=True)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    interest_type = models.CharField(max_length=20, null=True, blank=True)
    interest_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    title = models.CharField(max_length=30, null=True, blank=True)
    description = models.CharField(max_length=50, null=True, blank=True)
    popularity = models.CharField(max_length=20, null=True, blank=True)

    is_deleted   = models.BooleanField(default=False,verbose_name="Is Deleted",null=True,blank=True,)
    deleted_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True, related_name="investmentscheme_deletor")
    deleted_at   = models.DateTimeField(null=True)
    created_at   = models.DateTimeField(editable=False,default=timezone.now,verbose_name='Created At')
    modified_at  = models.DateTimeField(null=True,blank=True,verbose_name='Modified At')
    created_by   = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='Created By', related_name="investmentscheme_creater")
    modified_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='Modified By', related_name="investmentscheme_modifier")
    bkp_deleted_by = models.CharField(max_length=100, null=True, blank=True)
    bkp_created_by = models.CharField(max_length=100, null=True, blank=True)
    bkp_modified_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.scheme_type} Investment Scheme"

class UserInvestment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='Modified By', related_name="userinvestment_user")
    bkp_user = models.CharField(max_length=100, null=True, blank=True)
    scheme = models.ForeignKey(InvestmentScheme, on_delete=models.SET_NULL, null=True,blank=True,verbose_name='Modified By', related_name="userinvestment_plane")
    invested_amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.plan.name}"
