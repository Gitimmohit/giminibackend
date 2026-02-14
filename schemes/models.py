from django.db import models
from ems.models import *
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from django.db.models import Sum, Count
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
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    WITHDRAW_STATUS = [
        ("ACTIVE", "Active"),
        ("WITHDRAW_REQUESTED", "Withdraw Requested"),
        ("WITHDRAWN", "Withdrawn"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="investments"
    )

    scheme = models.ForeignKey(
        InvestmentScheme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scheme_investments"
    )

    invested_amount = models.DecimalField(max_digits=12, decimal_places=2)

    start_date = models.DateField(default=timezone.localdate)
    lock_in_end_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    withdraw_status = models.CharField(max_length=30, choices=WITHDRAW_STATUS, default="ACTIVE")
    is_withdrawn = models.BooleanField(default=False)
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.lock_in_end_date:
            self.lock_in_end_date = self.start_date + timedelta(days=365 * 3)
        super().save(*args, **kwargs)

    def is_lockin_completed(self):
        return timezone.localdate() >= self.lock_in_end_date

    def calculate_penalty(self):
        if not self.is_lockin_completed():
            return self.invested_amount * Decimal("0.10")
        return Decimal("0.00")

    def __str__(self):
        return f"{self.user} - {self.scheme}"

class ReferralCommission(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    from_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="commission_from"
    )
    investment = models.ForeignKey(UserInvestment, on_delete=models.CASCADE)

    level = models.PositiveSmallIntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2)

    payout_month = models.DateField()
    is_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    is_blocked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "investment", "level")
