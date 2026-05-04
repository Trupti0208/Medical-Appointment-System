from django.contrib import admin
from .models import Appointment, AppointmentReschedule, MedicalRecord, AppointmentReview

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'time_slot', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'appointment_date', 'doctor', 'is_first_visit')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__email', 'doctor__name', 'reason_for_visit')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('patient', 'doctor', 'appointment_date', 'time_slot', 'status')
        }),
        ('Medical Information', {
            'fields': ('reason_for_visit', 'symptoms', 'medical_history', 'is_first_visit')
        }),
        ('Payment Information', {
            'fields': ('consultation_fee', 'payment_status')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'doctor', 'time_slot')

@admin.register(AppointmentReschedule)
class AppointmentRescheduleAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'original_date', 'new_date', 'requested_by', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'requested_by')
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name', 'reason')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('appointment', 'original_date', 'original_time_slot', 'new_date', 'new_time_slot')
        }),
        ('Request Information', {
            'fields': ('requested_by', 'reason', 'status')
        }),
        ('Approval Information', {
            'fields': ('approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('appointment', 'requested_by', 'approved_by')

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'diagnosis', 'follow_up_needed', 'created_at')
    list_filter = ('follow_up_needed', 'created_at')
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name', 'diagnosis')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Diagnosis Information', {
            'fields': ('appointment', 'diagnosis', 'symptoms_observed')
        }),
        ('Treatment Information', {
            'fields': ('treatment_plan', 'medications_prescribed')
        }),
        ('Follow-up Information', {
            'fields': ('follow_up_needed', 'follow_up_date', 'follow_up_notes')
        }),
        ('Additional Information', {
            'fields': ('doctor_notes', 'vital_signs')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('appointment')

@admin.register(AppointmentReview)
class AppointmentReviewAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'rating', 'wait_time_rating', 'doctor_care_rating', 'staff_courtesy_rating', 'would_recommend', 'created_at')
    list_filter = ('rating', 'wait_time_rating', 'doctor_care_rating', 'staff_courtesy_rating', 'would_recommend', 'created_at')
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name', 'comment')
    readonly_fields = ('created_at', 'updated_at', 'average_rating')
    
    fieldsets = (
        ('Review Details', {
            'fields': ('appointment', 'rating', 'comment')
        }),
        ('Service Quality Ratings', {
            'fields': ('wait_time_rating', 'doctor_care_rating', 'staff_courtesy_rating', 'would_recommend')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'average_rating'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('appointment')
