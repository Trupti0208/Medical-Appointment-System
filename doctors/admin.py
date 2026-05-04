from django.contrib import admin
from .models import DoctorProfile, TimeSlot, DoctorReview

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'specialization', 'phone', 'is_available', 'created_at')
    list_filter = ('specialization', 'is_available', 'created_at')
    search_fields = ('name', 'email', 'specialization', 'clinic_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'email', 'phone', 'profile_picture')
        }),
        ('Professional Information', {
            'fields': ('specialization', 'qualifications', 'experience_years', 'license_number')
        }),
        ('Clinic Information', {
            'fields': ('clinic_name', 'clinic_address', 'consultation_fee')
        }),
        ('Availability', {
            'fields': ('is_available', 'max_appointments_per_day')
        }),
        ('Profile Details', {
            'fields': ('bio',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'get_day_of_week_display', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available', 'doctor')
    search_fields = ('doctor__name',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('doctor')

@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'doctor')
    search_fields = ('doctor__name', 'patient__first_name', 'patient__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('doctor', 'patient')
