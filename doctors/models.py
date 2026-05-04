from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DoctorProfile(models.Model):
    """Extended profile for doctor users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    
    # Basic Information
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Professional Information
    specialization = models.CharField(max_length=100)
    qualifications = models.TextField(help_text="List of medical qualifications and degrees")
    experience_years = models.IntegerField(default=0)
    license_number = models.CharField(max_length=50, unique=True)
    
    # Clinic/Hospital Information
    clinic_name = models.CharField(max_length=200, blank=True, null=True)
    clinic_address = models.TextField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Availability Settings
    is_available = models.BooleanField(default=True)
    max_appointments_per_day = models.IntegerField(default=10)
    
    # Profile Details
    bio = models.TextField(blank=True, null=True, help_text="Professional biography")
    profile_picture = models.ImageField(upload_to='doctor_profiles/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctors_profile'
        verbose_name = 'Doctor Profile'
        verbose_name_plural = 'Doctor Profiles'
        ordering = ['name']
    
    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"
    
    @property
    def full_name(self):
        return self.name
    
    def get_available_slots(self, date):
        """Get available time slots for a given date"""
        from appointments.models import TimeSlot, Appointment
        
        # Get all time slots for this doctor
        all_slots = TimeSlot.objects.filter(doctor=self, is_available=True)
        
        # Filter out booked slots for the given date
        booked_slots = Appointment.objects.filter(
            doctor=self,
            appointment_date=date,
            status__in=['SCHEDULED', 'CONFIRMED']
        ).values_list('time_slot', flat=True)
        
        available_slots = all_slots.exclude(id__in=booked_slots)
        return available_slots

class TimeSlot(models.Model):
    """Time slots for doctor availability"""
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='time_slots')
    
    # Time Information
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_week = models.IntegerField(
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday'),
        ]
    )
    
    # Availability
    is_available = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctors_time_slots'
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'
        ordering = ['day_of_week', 'start_time']
        unique_together = ['doctor', 'day_of_week', 'start_time']
    
    def __str__(self):
        day_name = self.get_day_of_week_display()
        return f"{self.doctor.name} - {day_name} {self.start_time} to {self.end_time}"
    
    @property
    def time_range(self):
        return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"

class DoctorReview(models.Model):
    """Patient reviews for doctors"""
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='reviews')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_reviews')
    
    # Review Details
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctors_reviews'
        verbose_name = 'Doctor Review'
        verbose_name_plural = 'Doctor Reviews'
        unique_together = ['doctor', 'patient']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.doctor.name} by {self.patient.full_name} - {self.rating} stars"
