from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import DoctorProfile, TimeSlot, DoctorReview
from .serializers import (
    DoctorProfileSerializer, DoctorProfileCreateSerializer,
    DoctorProfileUpdateSerializer, TimeSlotSerializer, TimeSlotCreateSerializer,
    DoctorReviewSerializer, DoctorReviewCreateSerializer
)
from accounts.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly

User = get_user_model()

class DoctorProfileListView(generics.ListAPIView):
    """API endpoint for listing all available doctors"""
    queryset = DoctorProfile.objects.filter(is_available=True)
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'is_available']
    search_fields = ['name', 'specialization', 'clinic_name']
    ordering_fields = ['name', 'created_at', 'average_rating']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        specialization = self.request.query_params.get('specialization', None)
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)
        return queryset.select_related('user').prefetch_related('time_slots', 'reviews')

class DoctorProfileDetailView(generics.RetrieveAPIView):
    """API endpoint for retrieving a specific doctor's profile"""
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.select_related('user').prefetch_related('time_slots', 'reviews')

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def doctor_available_slots(request, doctor_id):
    """API endpoint for getting available time slots for a doctor"""
    try:
        doctor = DoctorProfile.objects.get(id=doctor_id, is_available=True)
        date = request.query_params.get('date')
        
        if not date:
            return Response({'error': 'Date parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from datetime import datetime
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = target_date.weekday()
        
        # Get all time slots for this day
        time_slots = TimeSlot.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_available=True
        ).order_by('start_time')
        
        # Check which slots are already booked
        from appointments.models import Appointment
        booked_slot_ids = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=target_date,
            status__in=['SCHEDULED', 'CONFIRMED']
        ).values_list('time_slot_id', flat=True)
        
        available_slots = time_slots.exclude(id__in=booked_slot_ids)
        serializer = TimeSlotSerializer(available_slots, many=True)
        
        return Response({
            'doctor': DoctorProfileSerializer(doctor).data,
            'date': date,
            'available_slots': serializer.data
        })
        
    except DoctorProfile.DoesNotExist:
        return Response({'error': 'Doctor not found or not available'}, status=status.HTTP_404_NOT_FOUND)

class DoctorProfileCreateView(generics.CreateAPIView):
    """API endpoint for creating doctor profiles (admin only)"""
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

class DoctorProfileUpdateView(generics.RetrieveUpdateAPIView):
    """API endpoint for updating doctor profiles"""
    serializer_class = DoctorProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Doctors can only update their own profile
        if self.request.user.role == 'DOCTOR':
            try:
                return DoctorProfile.objects.get(user=self.request.user)
            except DoctorProfile.DoesNotExist:
                return None
        # Admins can update any profile
        elif self.request.user.role == 'ADMIN':
            return DoctorProfile.objects.get(pk=self.kwargs['pk'])
        return None
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DoctorProfileSerializer
        return DoctorProfileUpdateSerializer

class TimeSlotListCreateView(generics.ListCreateAPIView):
    """API endpoint for listing and creating time slots"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return TimeSlot.objects.filter(doctor_id=doctor_id).order_by('day_of_week', 'start_time')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TimeSlotCreateSerializer
        return TimeSlotSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        doctor_id = self.kwargs['doctor_id']
        try:
            doctor = DoctorProfile.objects.get(id=doctor_id)
            context['doctor'] = doctor
        except DoctorProfile.DoesNotExist:
            pass
        return context
    
    def perform_create(self, serializer):
        doctor_id = self.kwargs['doctor_id']
        doctor = DoctorProfile.objects.get(id=doctor_id)
        serializer.save(doctor=doctor)

class TimeSlotDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving, updating, and deleting time slots"""
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        doctor_id = self.kwargs['doctor_id']
        slot_id = self.kwargs['slot_id']
        return TimeSlot.objects.get(doctor_id=doctor_id, id=slot_id)

class DoctorReviewListCreateView(generics.ListCreateAPIView):
    """API endpoint for listing and creating doctor reviews"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        doctor_id = self.kwargs['doctor_id']
        return DoctorReview.objects.filter(doctor_id=doctor_id).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DoctorReviewCreateSerializer
        return DoctorReviewSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        doctor_id = self.kwargs['doctor_id']
        try:
            doctor = DoctorProfile.objects.get(id=doctor_id)
            context['doctor'] = doctor
            context['patient'] = self.request.user
        except DoctorProfile.DoesNotExist:
            pass
        return context

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def doctor_specializations(request):
    """API endpoint for getting all available specializations"""
    specializations = DoctorProfile.objects.values_list('specialization', flat=True).distinct()
    return Response({'specializations': list(specializations)})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_doctor_profile(request):
    """API endpoint for doctors to get their own profile"""
    if request.user.role != 'DOCTOR':
        return Response({'error': 'Only doctors can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        profile = DoctorProfile.objects.get(user=request.user)
        serializer = DoctorProfileSerializer(profile)
        return Response(serializer.data)
    except DoctorProfile.DoesNotExist:
        return Response({'error': 'Doctor profile not found'}, status=status.HTTP_404_NOT_FOUND)
