from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DoctorProfile, TimeSlot, DoctorReview

User = get_user_model()

class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for doctor time slots"""
    time_range = serializers.ReadOnlyField()
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = ('id', 'start_time', 'end_time', 'day_of_week', 'day_name', 'time_range', 'is_available')

class DoctorReviewSerializer(serializers.ModelSerializer):
    """Serializer for doctor reviews"""
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = DoctorReview
        fields = ('id', 'patient', 'patient_name', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'created_at')

class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for doctor profiles"""
    user_info = serializers.SerializerMethodField()
    time_slots = TimeSlotSerializer(many=True, read_only=True)
    reviews = DoctorReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorProfile
        fields = (
            'id', 'user', 'user_info', 'name', 'email', 'phone', 'specialization',
            'qualifications', 'experience_years', 'license_number', 'clinic_name',
            'clinic_address', 'consultation_fee', 'is_available', 'max_appointments_per_day',
            'bio', 'profile_picture', 'time_slots', 'reviews', 'average_rating',
            'total_reviews', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def get_user_info(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'email': obj.user.email,
                'role': obj.user.role
            }
        return None
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def get_total_reviews(self, obj):
        return obj.reviews.count()

class DoctorProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating doctor profiles (admin only)"""
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = DoctorProfile
        fields = (
            'user_id', 'name', 'email', 'phone', 'specialization',
            'qualifications', 'experience_years', 'license_number',
            'clinic_name', 'clinic_address', 'consultation_fee',
            'is_available', 'max_appointments_per_day', 'bio', 'profile_picture'
        )
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        try:
            user = User.objects.get(id=user_id, role='DOCTOR')
            return DoctorProfile.objects.create(user=user, **validated_data)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found or not a doctor")

class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating doctor profiles"""
    class Meta:
        model = DoctorProfile
        fields = (
            'name', 'phone', 'specialization', 'qualifications',
            'experience_years', 'clinic_name', 'clinic_address',
            'consultation_fee', 'is_available', 'max_appointments_per_day',
            'bio', 'profile_picture'
        )
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class TimeSlotCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating time slots"""
    class Meta:
        model = TimeSlot
        fields = ('start_time', 'end_time', 'day_of_week', 'is_available')
    
    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time")
        
        # Check for overlapping slots
        doctor = self.context['doctor']
        day_of_week = attrs.get('day_of_week')
        
        overlapping = TimeSlot.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()
        
        if overlapping:
            raise serializers.ValidationError("This time slot overlaps with an existing slot")
        
        return attrs

class DoctorReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating doctor reviews"""
    class Meta:
        model = DoctorReview
        fields = ('rating', 'comment')
    
    def create(self, validated_data):
        doctor = self.context['doctor']
        patient = self.context['patient']
        
        # Check if patient already reviewed this doctor
        if DoctorReview.objects.filter(doctor=doctor, patient=patient).exists():
            raise serializers.ValidationError("You have already reviewed this doctor")
        
        return DoctorReview.objects.create(
            doctor=doctor,
            patient=patient,
            **validated_data
        )
