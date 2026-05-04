from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Appointment, AppointmentReschedule, MedicalRecord, AppointmentReview
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer, AppointmentUpdateSerializer,
    AppointmentRescheduleSerializer, AppointmentRescheduleCreateSerializer,
    MedicalRecordSerializer, MedicalRecordCreateSerializer,
    AppointmentReviewSerializer, AppointmentReviewCreateSerializer
)

User = get_user_model()

class AppointmentListCreateView(generics.ListCreateAPIView):
    """API endpoint for listing and creating appointments"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'doctor', 'appointment_date']
    search_fields = ['reason_for_visit', 'doctor__name']
    ordering_fields = ['appointment_date', 'created_at', 'time_slot__start_time']
    ordering = ['-appointment_date', '-time_slot__start_time']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return Appointment.objects.filter(patient=user).select_related('doctor', 'time_slot', 'patient')
        elif user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor__user=user).select_related('doctor', 'time_slot', 'patient')
        elif user.role == 'ADMIN':
            return Appointment.objects.all().select_related('doctor', 'time_slot', 'patient')
        return Appointment.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentSerializer

class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving, updating, and deleting appointments"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return Appointment.objects.filter(patient=user).select_related('doctor', 'time_slot', 'patient')
        elif user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor__user=user).select_related('doctor', 'time_slot', 'patient')
        elif user.role == 'ADMIN':
            return Appointment.objects.all().select_related('doctor', 'time_slot', 'patient')
        return Appointment.objects.none()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AppointmentUpdateSerializer
        return AppointmentSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_appointment(request, appointment_id):
    """API endpoint for cancelling an appointment"""
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check permissions
        if request.user.role == 'PATIENT' and appointment.patient != request.user:
            return Response({'error': 'You can only cancel your own appointments'}, status=status.HTTP_403_FORBIDDEN)
        elif request.user.role == 'DOCTOR' and appointment.doctor.user != request.user:
            return Response({'error': 'You can only cancel your own appointments'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if appointment can be cancelled
        if not appointment.can_cancel:
            return Response({'error': 'This appointment cannot be cancelled (less than 24 hours before)'}, status=status.HTTP_400_BAD_REQUEST)
        
        appointment.status = 'CANCELLED'
        appointment.save()
        
        # Create notification
        from notifications.models import Notification
        if request.user.role == 'PATIENT':
            # Notify doctor
            Notification.objects.create(
                user=appointment.doctor.user,
                title='Appointment Cancelled',
                message=f'Appointment with {appointment.patient.full_name} on {appointment.appointment_date} has been cancelled',
                notification_type='APPOINTMENT_CANCELLED',
                related_appointment=appointment
            )
        else:
            # Notify patient
            Notification.objects.create(
                user=appointment.patient,
                title='Appointment Cancelled',
                message=f'Your appointment with Dr. {appointment.doctor.name} on {appointment.appointment_date} has been cancelled',
                notification_type='APPOINTMENT_CANCELLED',
                related_appointment=appointment
            )
        
        serializer = AppointmentSerializer(appointment)
        return Response({
            'message': 'Appointment cancelled successfully',
            'appointment': serializer.data
        })
        
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reschedule_appointment(request, appointment_id):
    """API endpoint for requesting appointment reschedule"""
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check permissions
        if request.user.role != 'PATIENT' or appointment.patient != request.user:
            return Response({'error': 'Only patients can request rescheduling for their own appointments'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if appointment can be rescheduled
        if not appointment.can_reschedule:
            return Response({'error': 'This appointment cannot be rescheduled'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AppointmentRescheduleCreateSerializer(
            data=request.data,
            context={'appointment': appointment, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        reschedule = serializer.save()
        
        return Response({
            'message': 'Reschedule request submitted successfully',
            'reschedule': AppointmentRescheduleSerializer(reschedule).data
        }, status=status.HTTP_201_CREATED)
        
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_appointments(request):
    """API endpoint for getting current user's appointments"""
    user = request.user
    
    if user.role == 'PATIENT':
        appointments = Appointment.objects.filter(patient=user).select_related('doctor', 'time_slot')
    elif user.role == 'DOCTOR':
        appointments = Appointment.objects.filter(doctor__user=user).select_related('doctor', 'time_slot', 'patient')
    else:
        appointments = Appointment.objects.all().select_related('doctor', 'time_slot', 'patient')
    
    # Filter by date if provided
    date_filter = request.query_params.get('date')
    if date_filter:
        try:
            filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(appointment_date=filter_date)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Filter by status if provided
    status_filter = request.query_params.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def appointment_dashboard(request):
    """API endpoint for appointment dashboard statistics"""
    user = request.user
    
    if user.role == 'PATIENT':
        total_appointments = Appointment.objects.filter(patient=user).count()
        upcoming_appointments = Appointment.objects.filter(
            patient=user,
            appointment_date__gte=timezone.now().date(),
            status__in=['SCHEDULED', 'CONFIRMED']
        ).count()
        completed_appointments = Appointment.objects.filter(
            patient=user,
            status='COMPLETED'
        ).count()
        
    elif user.role == 'DOCTOR':
        try:
            from doctors.models import DoctorProfile
            doctor_profile = DoctorProfile.objects.get(user=user)
            
            total_appointments = Appointment.objects.filter(doctor=doctor_profile).count()
            today_appointments = Appointment.objects.filter(
                doctor=doctor_profile,
                appointment_date=timezone.now().date()
            ).count()
            upcoming_appointments = Appointment.objects.filter(
                doctor=doctor_profile,
                appointment_date__gte=timezone.now().date(),
                status__in=['SCHEDULED', 'CONFIRMED']
            ).count()
            
            return Response({
                'total_appointments': total_appointments,
                'today_appointments': today_appointments,
                'upcoming_appointments': upcoming_appointments
            })
        except DoctorProfile.DoesNotExist:
            return Response({'error': 'Doctor profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    else:  # ADMIN
        total_appointments = Appointment.objects.count()
        today_appointments = Appointment.objects.filter(appointment_date=timezone.now().date()).count()
        pending_appointments = Appointment.objects.filter(status='PENDING').count()
        
        return Response({
            'total_appointments': total_appointments,
            'today_appointments': today_appointments,
            'pending_appointments': pending_appointments
        })
    
    return Response({
        'total_appointments': total_appointments,
        'upcoming_appointments': upcoming_appointments,
        'completed_appointments': completed_appointments
    })

class AppointmentRescheduleListView(generics.ListAPIView):
    """API endpoint for listing reschedule requests"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentRescheduleSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return AppointmentReschedule.objects.filter(
                appointment__doctor__user=user
            ).select_related('appointment', 'requested_by', 'original_time_slot', 'new_time_slot')
        elif user.role == 'PATIENT':
            return AppointmentReschedule.objects.filter(
                requested_by=user
            ).select_related('appointment', 'original_time_slot', 'new_time_slot')
        elif user.role == 'ADMIN':
            return AppointmentReschedule.objects.all().select_related('appointment', 'requested_by', 'original_time_slot', 'new_time_slot')
        return AppointmentReschedule.objects.none()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_reschedule(request, reschedule_id):
    """API endpoint for approving reschedule requests (doctor only)"""
    try:
        reschedule = AppointmentReschedule.objects.get(id=reschedule_id)
        
        # Check permissions (only doctor can approve)
        if request.user.role != 'DOCTOR' or reschedule.appointment.doctor.user != request.user:
            return Response({'error': 'Only the doctor can approve reschedule requests'}, status=status.HTTP_403_FORBIDDEN)
        
        if reschedule.status != 'PENDING':
            return Response({'error': 'This reschedule request has already been processed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the appointment
        appointment = reschedule.appointment
        appointment.appointment_date = reschedule.new_date
        appointment.time_slot = reschedule.new_time_slot
        appointment.status = 'RESCHEDULED'
        appointment.save()
        
        # Update reschedule request
        reschedule.status = 'APPROVED'
        reschedule.approved_by = request.user
        reschedule.approved_at = timezone.now()
        reschedule.save()
        
        # Create notification for patient
        from notifications.models import Notification
        Notification.objects.create(
            user=appointment.patient,
            title='Reschedule Request Approved',
            message=f'Your appointment reschedule request has been approved. New appointment: {appointment.appointment_date} at {appointment.time_slot.start_time}',
            notification_type='APPOINTMENT_RESCHEDULED',
            related_appointment=appointment
        )
        
        return Response({
            'message': 'Reschedule request approved successfully',
            'appointment': AppointmentSerializer(appointment).data
        })
        
    except AppointmentReschedule.DoesNotExist:
        return Response({'error': 'Reschedule request not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_reschedule(request, reschedule_id):
    """API endpoint for rejecting reschedule requests (doctor only)"""
    try:
        reschedule = AppointmentReschedule.objects.get(id=reschedule_id)
        rejection_reason = request.data.get('rejection_reason', '')
        
        # Check permissions (only doctor can reject)
        if request.user.role != 'DOCTOR' or reschedule.appointment.doctor.user != request.user:
            return Response({'error': 'Only the doctor can reject reschedule requests'}, status=status.HTTP_403_FORBIDDEN)
        
        if reschedule.status != 'PENDING':
            return Response({'error': 'This reschedule request has already been processed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update reschedule request
        reschedule.status = 'REJECTED'
        reschedule.approved_by = request.user
        reschedule.approved_at = timezone.now()
        reschedule.rejection_reason = rejection_reason
        reschedule.save()
        
        # Create notification for patient
        from notifications.models import Notification
        Notification.objects.create(
            user=reschedule.requested_by,
            title='Reschedule Request Rejected',
            message=f'Your appointment reschedule request has been rejected. Reason: {rejection_reason}',
            notification_type='APPOINTMENT_RESCHEDULED',
            related_appointment=reschedule.appointment
        )
        
        return Response({'message': 'Reschedule request rejected successfully'})
        
    except AppointmentReschedule.DoesNotExist:
        return Response({'error': 'Reschedule request not found'}, status=status.HTTP_404_NOT_FOUND)

class MedicalRecordListCreateView(generics.ListCreateAPIView):
    """API endpoint for listing and creating medical records"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return MedicalRecord.objects.filter(
                appointment__doctor__user=user
            ).select_related('appointment', 'appointment__patient')
        elif user.role == 'PATIENT':
            return MedicalRecord.objects.filter(
                appointment__patient=user
            ).select_related('appointment', 'appointment__doctor')
        elif user.role == 'ADMIN':
            return MedicalRecord.objects.all().select_related('appointment', 'appointment__patient', 'appointment__doctor')
        return MedicalRecord.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MedicalRecordCreateSerializer
        return MedicalRecordSerializer
    
    def perform_create(self, serializer):
        appointment_id = self.request.data.get('appointment')
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Only doctors can create medical records for their appointments
        if self.request.user.role != 'DOCTOR' or appointment.doctor.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only doctors can create medical records for their appointments")
        
        serializer.save(appointment=appointment)

class AppointmentReviewListCreateView(generics.ListCreateAPIView):
    """API endpoint for listing and creating appointment reviews"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return AppointmentReview.objects.filter(
                appointment__patient=user
            ).select_related('appointment', 'appointment__doctor')
        elif user.role in ['DOCTOR', 'ADMIN']:
            return AppointmentReview.objects.all().select_related('appointment', 'appointment__patient', 'appointment__doctor')
        return AppointmentReview.objects.none()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentReviewCreateSerializer
        return AppointmentReviewSerializer
    
    def perform_create(self, serializer):
        appointment_id = self.request.data.get('appointment')
        appointment = Appointment.objects.get(id=appointment_id)
        serializer.save(appointment=appointment)
