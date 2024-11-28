from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    ACCOUNT_TYPES = [
        ('individual', 'Individual'),
        ('institutional', 'Institutional'),
        ('verified', 'Verified')
    ]
    account_type = models.CharField(
        max_length=20, 
        choices=ACCOUNT_TYPES, 
        default='individual'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class UserFinancialProfile(models.Model):
    EXPERIENCE_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('professional', 'Professional')
    ]

    RISK_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]

    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='financial_profile'
    )
    investment_experience = models.CharField(
        max_length=20, 
        choices=EXPERIENCE_LEVELS, 
        null=True, 
        blank=True
    )
    risk_tolerance = models.CharField(
        max_length=10, 
        choices=RISK_LEVELS, 
        null=True, 
        blank=True
    )
    preferred_sectors = models.JSONField(default=list)
    annual_income = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    net_worth = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"{self.user.username}'s Financial Profile"