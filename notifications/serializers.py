from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification, NotificationPreference, NotificationTemplate

User = get_user_model()

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    is_recent = serializers.ReadOnlyField()
    
    class Meta:
        model = Notification
        fields = (
            'id', 'user', 'user_name', 'title', 'message', 'notification_type',
            'related_appointment', 'related_doctor', 'related_patient',
            'is_read', 'is_important', 'priority', 'action_url', 'action_text',
            'created_at', 'read_at', 'expires_at', 'is_expired', 'is_recent'
        )
        read_only_fields = ('id', 'created_at', 'read_at')

class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    class Meta:
        model = Notification
        fields = (
            'user', 'title', 'message', 'notification_type',
            'related_appointment', 'related_doctor', 'related_patient',
            'is_important', 'priority', 'action_url', 'action_text', 'expires_at'
        )

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = (
            'id', 'user', 'user_name',
            'email_appointment_booked', 'email_appointment_cancelled', 'email_appointment_confirmed',
            'email_appointment_rescheduled', 'email_appointment_reminder', 'email_payment_received',
            'email_payment_failed', 'email_medical_record_updated', 'email_doctor_available',
            'email_system_announcements',
            'push_appointment_booked', 'push_appointment_cancelled', 'push_appointment_confirmed',
            'push_appointment_rescheduled', 'push_appointment_reminder', 'push_payment_received',
            'push_payment_failed', 'push_medical_record_updated', 'push_doctor_available',
            'push_system_announcements',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates"""
    class Meta:
        model = NotificationTemplate
        fields = (
            'id', 'notification_type', 'title_template', 'message_template',
            'action_url_template', 'action_text_template', 'default_priority',
            'default_is_important', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
