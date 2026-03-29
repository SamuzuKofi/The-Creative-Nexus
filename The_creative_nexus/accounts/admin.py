from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
         'fields': ('email_verified', 'email_verification_token')}),
    )
    list_display = ('email', 'username', 'email_verified',
                    'is_staff', 'created_at')
    list_filter = ('email_verified', 'is_staff', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_verified', 'location', 'created_at')
    list_filter = ('role', 'is_verified', 'created_at')
    search_fields = ('user__email', 'user__username', 'location', 'skills')
    readonly_fields = ('created_at', 'updated_at')
