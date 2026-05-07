from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_admin_user', 'created_at']
    list_filter = ['is_admin_user']
    search_fields = ['user__username', 'user__email']
