from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, HealthRecord, DailyReminderSetting, FoodRecommendation

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Role & Permissions', {'fields': ('role', 'is_verified', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Security', {'fields': ('last_login_ip', 'failed_login_attempts', 'account_locked_until')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'sleep_hours', 'water_intake', 'mood', 'created_by', 'last_modified')
    list_filter = ('mood', 'date', 'user__role')
    search_fields = ('user__username', 'notes')
    date_hierarchy = 'date'
    readonly_fields = ('last_modified',)
    
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Health Data', {'fields': ('sleep_hours', 'water_intake', 'mood', 'notes')}),
        ('Record Management', {'fields': ('created_by', 'last_modified_by', 'last_modified')}),
    )

@admin.register(DailyReminderSetting)
class DailyReminderSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'reminder_time', 'send_email', 'send_in_app')
    search_fields = ('user__username',)

admin.site.register(FoodRecommendation)
