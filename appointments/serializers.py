from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Appointment, AppointmentReschedule, MedicalRecord, AppointmentReview
from doctors.serializers import TimeSlotSerializer, DoctorProfileSerializer

User = get_user_model()

class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointments - minimal version to avoid validation issues"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    time_slot_start = serializers.CharField(source='time_slot.start_time', read_only=True)
    time_slot_end = serializers.CharField(source='time_slot.end_time', read_only=True)
    
    class Meta:
        model = Appointment
        fields = (
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name', 'doctor_specialization',
            'appointment_date', 'time_slot', 'time_slot_start', 'time_slot_end',
            'status', 'reason_for_visit', 'symptoms', 'medical_history', 'consultation_fee',
            'payment_status', 'notes', 'is_first_visit', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'consultation_fee', 'created_at', 'updated_at')

class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments"""
    class Meta:
        model = Appointment
        fields = (
            'doctor', 'appointment_date', 'time_slot', 'reason_for_visit',
            'symptoms', 'medical_history', 'is_first_visit'
        )
    
    def validate(self, attrs):
        doctor = attrs['doctor']
        appointment_date = attrs['appointment_date']
        time_slot = attrs['time_slot']
        
        # Check if appointment date is in the past
        if appointment_date < timezone.now().date():
            raise serializers.ValidationError("Cannot book appointments in the past")
        
        # Check if time slot belongs to the doctor and is available
        if time_slot.doctor != doctor:
            raise serializers.ValidationError("This time slot does not belong to the selected doctor")
        
        if not time_slot.is_available:
            raise serializers.ValidationError("This time slot is not available")
        
        # Check if time slot is for the correct day of week
        if time_slot.day_of_week != appointment_date.weekday():
            raise serializers.ValidationError("This time slot is not available on the selected date")
        
        # Check if slot is already booked
        if Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            time_slot=time_slot,
            status__in=['SCHEDULED', 'CONFIRMED']
        ).exists():
            raise serializers.ValidationError("This time slot is already booked")
        
        # Check if patient has any existing appointment at the same time
        patient = self.context['request'].user
        if Appointment.objects.filter(
            patient=patient,
            appointment_date=appointment_date,
            time_slot=time_slot,
            status__in=['SCHEDULED', 'CONFIRMED']
        ).exists():
            raise serializers.ValidationError("You already have an appointment at this time")
        
        return attrs
    
    def create(self, validated_data):
        patient = self.context['request'].user
        appointment = Appointment.objects.create(patient=patient, **validated_data)
        
        # Create notification for the doctor
        from notifications.models import Notification
        Notification.objects.create(
            user=appointment.doctor.user,
            title='New Appointment Booking',
            message=f'You have a new appointment booking with {patient.full_name} on {appointment.appointment_date} at {appointment.time_slot.start_time}',
            notification_type='APPOINTMENT_BOOKED',
            related_appointment=appointment
        )
        
        return appointment

class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating appointments"""
    class Meta:
        model = Appointment
        fields = ('status', 'notes', 'payment_status')
    
    def validate_status(self, value):
        user = self.context['request'].user
        current_status = self.instance.status if self.instance else None
        
        # Patients can only cancel their own appointments
        if user.role == 'PATIENT' and value not in ['CANCELLED']:
            if current_status != value:
                raise serializers.ValidationError("Patients can only cancel appointments")
        
        # Doctors can approve, reject, complete appointments
        if user.role == 'DOCTOR' and value not in ['CONFIRMED', 'CANCELLED', 'COMPLETED', 'NO_SHOW']:
            if current_status != value:
                raise serializers.ValidationError("Invalid status transition for doctor")
        
        return value
    
    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        
        # Update the appointment
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Create notifications for status changes
        if old_status != new_status:
            from notifications.models import Notification
            
            if new_status == 'CONFIRMED':
                # Notify patient that appointment is confirmed
                Notification.objects.create(
                    user=instance.patient,
                    title='Appointment Confirmed',
                    message=f'Your appointment with Dr. {instance.doctor.name} on {instance.appointment_date} at {instance.time_slot.start_time} has been confirmed.',
                    notification_type='APPOINTMENT_CONFIRMED',
                    related_appointment=instance
                )
            elif new_status == 'CANCELLED':
                # Notify the other party about cancellation
                if self.context['request'].user.role == 'DOCTOR':
                    Notification.objects.create(
                        user=instance.patient,
                        title='Appointment Cancelled by Doctor',
                        message=f'Your appointment with Dr. {instance.doctor.name} on {instance.appointment_date} has been cancelled by the doctor.',
                        notification_type='APPOINTMENT_CANCELLED',
                        related_appointment=instance
                    )
                else:
                    Notification.objects.create(
                        user=instance.doctor.user,
                        title='Appointment Cancelled by Patient',
                        message=f'Appointment with {instance.patient.full_name} on {instance.appointment_date} has been cancelled by the patient.',
                        notification_type='APPOINTMENT_CANCELLED',
                        related_appointment=instance
                    )
            elif new_status == 'COMPLETED':
                # Notify patient that appointment is completed
                Notification.objects.create(
                    user=instance.patient,
                    title='Appointment Completed',
                    message=f'Your appointment with Dr. {instance.doctor.name} on {instance.appointment_date} has been marked as completed.',
                    notification_type='APPOINTMENT_COMPLETED',
                    related_appointment=instance
                )
        
        return instance

class AppointmentRescheduleSerializer(serializers.ModelSerializer):
    """Serializer for appointment reschedule requests"""
    original_time_slot_info = TimeSlotSerializer(source='original_time_slot', read_only=True)
    new_time_slot_info = TimeSlotSerializer(source='new_time_slot', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    
    class Meta:
        model = AppointmentReschedule
        fields = (
            'id', 'appointment', 'original_date', 'original_time_slot', 'original_time_slot_info',
            'new_date', 'new_time_slot', 'new_time_slot_info', 'requested_by', 'requested_by_name',
            'reason', 'status', 'approved_by', 'approved_at', 'rejection_reason', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'requested_by', 'approved_by', 'approved_at', 'created_at', 'updated_at')

class AppointmentRescheduleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reschedule requests"""
    class Meta:
        model = AppointmentReschedule
        fields = ('new_date', 'new_time_slot', 'reason')
    
    def validate(self, attrs):
        appointment = self.context['appointment']
        new_date = attrs['new_date']
        new_time_slot = attrs['new_time_slot']
        
        # Check if appointment can be rescheduled
        if not appointment.can_reschedule:
            raise serializers.ValidationError("This appointment cannot be rescheduled")
        
        # Check if new date is in the past
        if new_date < timezone.now().date():
            raise serializers.ValidationError("Cannot reschedule to a past date")
        
        # Check if new time slot belongs to the same doctor
        if new_time_slot.doctor != appointment.doctor:
            raise serializers.ValidationError("New time slot must belong to the same doctor")
        
        if not new_time_slot.is_available:
            raise serializers.ValidationError("New time slot is not available")
        
        # Check if new time slot is for the correct day of week
        if new_time_slot.day_of_week != new_date.weekday():
            raise serializers.ValidationError("New time slot is not available on the selected date")
        
        # Check if new slot is already booked
        if Appointment.objects.filter(
            doctor=appointment.doctor,
            appointment_date=new_date,
            time_slot=new_time_slot,
            status__in=['SCHEDULED', 'CONFIRMED']
        ).exists():
            raise serializers.ValidationError("New time slot is already booked")
        
        return attrs
    
    def create(self, validated_data):
        appointment = self.context['appointment']
        requested_by = self.context['request'].user
        
        reschedule = AppointmentReschedule.objects.create(
            appointment=appointment,
            original_date=appointment.appointment_date,
            original_time_slot=appointment.time_slot,
            requested_by=requested_by,
            **validated_data
        )
        
        # Create notification for the doctor
        from notifications.models import Notification
        Notification.objects.create(
            user=appointment.doctor.user,
            title='Appointment Reschedule Request',
            message=f'{requested_by.full_name} has requested to reschedule their appointment from {appointment.appointment_date} to {reschedule.new_date}',
            notification_type='APPOINTMENT_RESCHEDULED',
            related_appointment=appointment
        )
        
        return reschedule

class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer for medical records"""
    appointment_info = AppointmentSerializer(source='appointment', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = (
            'id', 'appointment', 'appointment_info', 'diagnosis', 'symptoms_observed',
            'treatment_plan', 'medications_prescribed', 'follow_up_needed', 'follow_up_date',
            'follow_up_notes', 'doctor_notes', 'vital_signs', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating medical records"""
    class Meta:
        model = MedicalRecord
        fields = (
            'diagnosis', 'symptoms_observed', 'treatment_plan', 'medications_prescribed',
            'follow_up_needed', 'follow_up_date', 'follow_up_notes', 'doctor_notes', 'vital_signs'
        )
    
    def validate_follow_up_date(self, value):
        if value and value <= timezone.now().date():
            raise serializers.ValidationError("Follow-up date must be in the future")
        return value

class AppointmentReviewSerializer(serializers.ModelSerializer):
    """Serializer for appointment reviews"""
    appointment_info = AppointmentSerializer(source='appointment', read_only=True)
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = AppointmentReview
        fields = (
            'id', 'appointment', 'appointment_info', 'rating', 'comment', 'wait_time_rating',
            'doctor_care_rating', 'staff_courtesy_rating', 'would_recommend', 'average_rating',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

class AppointmentReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointment reviews"""
    class Meta:
        model = AppointmentReview
        fields = (
            'rating', 'comment', 'wait_time_rating', 'doctor_care_rating',
            'staff_courtesy_rating', 'would_recommend'
        )
    
    def validate(self, attrs):
        appointment = self.context['appointment']
        
        # Check if appointment is completed
        if appointment.status != 'COMPLETED':
            raise serializers.ValidationError("Can only review completed appointments")
        
        # Check if user is the patient
        if self.context['request'].user != appointment.patient:
            raise serializers.ValidationError("Only the patient can review their appointment")
        
        return attrs
