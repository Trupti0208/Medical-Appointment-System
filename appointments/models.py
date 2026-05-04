from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

class Appointment(models.Model):
    """Appointment model for scheduling patient-doctor meetings"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
        ('NO_SHOW', 'No Show'),
        ('RESCHEDULED', 'Rescheduled'),
    ]
    
    # Basic Information
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey('doctors.DoctorProfile', on_delete=models.CASCADE, related_name='doctor_appointments')
    
    # Appointment Details
    appointment_date = models.DateField()
    time_slot = models.ForeignKey('doctors.TimeSlot', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Medical Information
    reason_for_visit = models.TextField(help_text="Reason for the appointment")
    symptoms = models.TextField(blank=True, null=True, help_text="Describe symptoms or concerns")
    medical_history = models.TextField(blank=True, null=True, help_text="Relevant medical history")
    
    # Payment Information
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PAID', 'Paid'),
            ('REFUNDED', 'Refunded'),
        ],
        default='PENDING'
    )
    
    # Additional Information
    notes = models.TextField(blank=True, null=True, help_text="Additional notes for the appointment")
    is_first_visit = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointments_appointment'
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-appointment_date', '-time_slot__start_time']
        unique_together = ['doctor', 'appointment_date', 'time_slot']
    
    def __str__(self):
        return f"{self.patient.full_name} - Dr. {self.doctor.name} on {self.appointment_date} at {self.time_slot.start_time}"
    
    @property
    def appointment_datetime(self):
        """Combine date and time for full datetime"""
        import datetime
        return datetime.datetime.combine(self.appointment_date, self.time_slot.start_time)
    
    @property
    def is_past(self):
        """Check if appointment is in the past"""
        return self.appointment_datetime < timezone.now()
    
    @property
    def is_today(self):
        """Check if appointment is today"""
        return self.appointment_date == timezone.now().date()
    
    @property
    def can_cancel(self):
        """Check if appointment can be cancelled (24 hours before)"""
        if self.status in ['CANCELLED', 'COMPLETED', 'NO_SHOW']:
            return False
        
        import datetime
        cutoff_time = self.appointment_datetime - datetime.timedelta(hours=24)
        return timezone.now() < cutoff_time
    
    @property
    def can_reschedule(self):
        """Check if appointment can be rescheduled"""
        return self.can_cancel and self.status in ['SCHEDULED', 'CONFIRMED']
    
    def save(self, *args, **kwargs):
        # Set consultation fee from doctor's profile if not set
        if not self.consultation_fee and self.doctor:
            self.consultation_fee = self.doctor.consultation_fee
        
        super().save(*args, **kwargs)

class AppointmentReschedule(models.Model):
    """Track appointment reschedule requests and history"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    # Original and New Appointment Details
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reschedule_requests')
    original_date = models.DateField()
    original_time_slot = models.ForeignKey('doctors.TimeSlot', on_delete=models.CASCADE, related_name='original_reschedules')
    new_date = models.DateField()
    new_time_slot = models.ForeignKey('doctors.TimeSlot', on_delete=models.CASCADE, related_name='new_reschedules')
    
    # Request Details
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reschedule_requests')
    reason = models.TextField(help_text="Reason for rescheduling")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Approval Details
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_reschedules')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appointments_reschedule'
        verbose_name = 'Appointment Reschedule'
        verbose_name_plural = 'Appointment Reschedules'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reschedule request for {self.appointment} from {self.original_date} to {self.new_date}"

class MedicalRecord(models.Model):
    """Medical records for appointments"""
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='medical_record')
    
    # Diagnosis Information
    diagnosis = models.TextField(help_text="Doctor's diagnosis")
    symptoms_observed = models.TextField(blank=True, null=True)
    
    # Treatment Information
    treatment_plan = models.TextField(help_text="Treatment plan and recommendations")
    medications_prescribed = models.TextField(blank=True, null=True, help_text="List of prescribed medications")
    
    # Follow-up Information
    follow_up_needed = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True, null=True)
    
    # Additional Information
    doctor_notes = models.TextField(blank=True, null=True, help_text="Additional doctor notes")
    vital_signs = models.JSONField(default=dict, blank=True, help_text="Vital signs as JSON")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointments_medical_record'
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Medical record for {self.appointment}"

class AppointmentReview(models.Model):
    """Patient reviews for completed appointments"""
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='appointment_review')
    
    # Review Details
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(blank=True, null=True)
    
    # Service Quality
    wait_time_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Wait time rating from 1 to 5"
    )
    doctor_care_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Doctor care rating from 1 to 5"
    )
    staff_courtesy_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Staff courtesy rating from 1 to 5"
    )
    
    # Recommendations
    would_recommend = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointments_review'
        verbose_name = 'Appointment Review'
        verbose_name_plural = 'Appointment Reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.appointment} - {self.rating} stars"
    
    @property
    def average_rating(self):
        """Calculate average of all ratings"""
        total = self.rating + self.wait_time_rating + self.doctor_care_rating + self.staff_courtesy_rating
        return total / 4
