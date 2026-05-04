from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Notification(models.Model):
    """Notification model for user notifications"""
    
    NOTIFICATION_TYPES = [
        ('APPOINTMENT_BOOKED', 'Appointment Booked'),
        ('APPOINTMENT_CANCELLED', 'Appointment Cancelled'),
        ('APPOINTMENT_CONFIRMED', 'Appointment Confirmed'),
        ('APPOINTMENT_RESCHEDULED', 'Appointment Rescheduled'),
        ('APPOINTMENT_REMINDER', 'Appointment Reminder'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('PAYMENT_FAILED', 'Payment Failed'),
        ('MEDICAL_RECORD_UPDATED', 'Medical Record Updated'),
        ('DOCTOR_AVAILABLE', 'Doctor Available'),
        ('SYSTEM_ANNOUNCEMENT', 'System Announcement'),
    ]
    
    # Recipient and Content
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    
    # Related Objects (optional)
    related_appointment = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    related_doctor = models.ForeignKey('doctors.DoctorProfile', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    related_patient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='patient_notifications')
    
    # Status and Priority
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=10,
        choices=[
            ('LOW', 'Low'),
            ('MEDIUM', 'Medium'),
            ('HIGH', 'High'),
            ('URGENT', 'Urgent'),
        ],
        default='MEDIUM'
    )
    
    # Action URLs (optional)
    action_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL to redirect when notification is clicked")
    action_text = models.CharField(max_length=50, blank=True, null=True, help_text="Text for action button")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Notification expires at this time")
    
    class Meta:
        db_table = 'notifications_notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['notification_type', 'created_at']),
            models.Index(fields=['priority', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_recent(self):
        """Check if notification is recent (created within last 24 hours)"""
        return self.created_at >= timezone.now() - timezone.timedelta(hours=24)
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])

class NotificationPreference(models.Model):
    """User notification preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notification preferences
    email_appointment_booked = models.BooleanField(default=True)
    email_appointment_cancelled = models.BooleanField(default=True)
    email_appointment_confirmed = models.BooleanField(default=True)
    email_appointment_rescheduled = models.BooleanField(default=True)
    email_appointment_reminder = models.BooleanField(default=True)
    email_payment_received = models.BooleanField(default=True)
    email_payment_failed = models.BooleanField(default=True)
    email_medical_record_updated = models.BooleanField(default=True)
    email_doctor_available = models.BooleanField(default=True)
    email_system_announcements = models.BooleanField(default=True)
    
    # Push notification preferences (for future implementation)
    push_appointment_booked = models.BooleanField(default=True)
    push_appointment_cancelled = models.BooleanField(default=True)
    push_appointment_confirmed = models.BooleanField(default=True)
    push_appointment_rescheduled = models.BooleanField(default=True)
    push_appointment_reminder = models.BooleanField(default=True)
    push_payment_received = models.BooleanField(default=True)
    push_payment_failed = models.BooleanField(default=True)
    push_medical_record_updated = models.BooleanField(default=True)
    push_doctor_available = models.BooleanField(default=True)
    push_system_announcements = models.BooleanField(default=True)
    
    # General preferences
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(default='22:00:00')
    quiet_hours_end = models.TimeField(default='08:00:00')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications_preference'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Notification preferences for {self.user.email}"
    
    def should_send_notification(self, notification_type, channel='email'):
        """Check if user should receive notification of specific type via specific channel"""
        # Check quiet hours
        if self.quiet_hours_enabled:
            current_time = timezone.now().time()
            if self.quiet_hours_start <= self.quiet_hours_end:
                # Quiet hours don't cross midnight (e.g., 22:00 to 08:00)
                if self.quiet_hours_start <= current_time <= self.quiet_hours_end:
                    return False
            else:
                # Quiet hours cross midnight (e.g., 22:00 to 08:00)
                if current_time >= self.quiet_hours_start or current_time <= self.quiet_hours_end:
                    return False
        
        # Check notification type preference
        preference_field = f"{channel}_{notification_type.lower()}"
        return getattr(self, preference_field, True)

class NotificationTemplate(models.Model):
    """Templates for different notification types"""
    
    notification_type = models.CharField(max_length=30, choices=Notification.NOTIFICATION_TYPES, unique=True)
    title_template = models.CharField(max_length=200, help_text="Template for notification title. Use {variable} placeholders")
    message_template = models.TextField(help_text="Template for notification message. Use {variable} placeholders")
    action_url_template = models.URLField(max_length=500, blank=True, null=True, help_text="Template for action URL")
    action_text_template = models.CharField(max_length=50, blank=True, null=True, help_text="Template for action text")
    
    # Default settings
    default_priority = models.CharField(
        max_length=10,
        choices=[
            ('LOW', 'Low'),
            ('MEDIUM', 'Medium'),
            ('HIGH', 'High'),
            ('URGENT', 'Urgent'),
        ],
        default='MEDIUM'
    )
    default_is_important = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications_template'
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
    
    def __str__(self):
        return f"Template for {self.get_notification_type_display()}"
    
    def render_title(self, context):
        """Render title template with context variables"""
        return self.title_template.format(**context)
    
    def render_message(self, context):
        """Render message template with context variables"""
        return self.message_template.format(**context)
    
    def render_action_url(self, context):
        """Render action URL template with context variables"""
        if self.action_url_template:
            return self.action_url_template.format(**context)
        return None
    
    def render_action_text(self, context):
        """Render action text template with context variables"""
        if self.action_text_template:
            return self.action_text_template.format(**context)
        return None
