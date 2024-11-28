from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserFinancialProfile

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'full_name', 'is_staff', 'is_active', 'account_type')
    list_filter = ('is_staff', 'is_active', 'account_type')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'account_type')}),
        ('Important dates', {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active', 'account_type')
        }),
    )
    search_fields = ('email', 'username', 'full_name')
    ordering = ('email',)

class UserFinancialProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'investment_experience', 'risk_tolerance', 'annual_income', 'net_worth')
    list_filter = ('investment_experience', 'risk_tolerance')
    search_fields = ('user__email', 'user__username')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserFinancialProfile, UserFinancialProfileAdmin)

# Register your models here.
