from django.contrib import admin
from .models import Notification, NotificationPreference, NotificationTemplate

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'priority', 'created_at')
    list_filter = ('notification_type', 'is_read', 'priority', 'is_important', 'created_at')
    search_fields = ('title', 'message', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'read_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Related Objects', {
            'fields': ('related_appointment', 'related_doctor', 'related_patient')
        }),
        ('Status and Priority', {
            'fields': ('is_read', 'is_important', 'priority')
        }),
        ('Action Settings', {
            'fields': ('action_url', 'action_text')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'read_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end', 'updated_at')
    list_filter = ('quiet_hours_enabled', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Notifications', {
            'fields': (
                'email_appointment_booked', 'email_appointment_cancelled', 'email_appointment_confirmed',
                'email_appointment_rescheduled', 'email_appointment_reminder', 'email_payment_received',
                'email_payment_failed', 'email_medical_record_updated', 'email_doctor_available',
                'email_system_announcements'
            )
        }),
        ('Push Notifications', {
            'fields': (
                'push_appointment_booked', 'push_appointment_cancelled', 'push_appointment_confirmed',
                'push_appointment_rescheduled', 'push_appointment_reminder', 'push_payment_received',
                'push_payment_failed', 'push_medical_record_updated', 'push_doctor_available',
                'push_system_announcements'
            )
        }),
        ('General Preferences', {
            'fields': ('quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'title_template', 'default_priority', 'default_is_important', 'updated_at')
    list_filter = ('notification_type', 'default_priority', 'default_is_important')
    search_fields = ('title_template', 'message_template')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Template Type', {
            'fields': ('notification_type',)
        }),
        ('Content Templates', {
            'fields': ('title_template', 'message_template', 'action_url_template', 'action_text_template')
        }),
        ('Default Settings', {
            'fields': ('default_priority', 'default_is_important')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
