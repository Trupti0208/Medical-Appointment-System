from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

class FlexibleDateField(serializers.DateField):
    """Custom date field that handles empty strings properly"""
    def to_internal_value(self, data):
        if data == '' or data is None:
            return None
        return super().to_internal_value(data)

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    date_of_birth = FlexibleDateField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'role', 'phone', 'date_of_birth', 'address')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
            
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        # Handle empty date_of_birth by setting it to None if it's an empty string
        if 'date_of_birth' in validated_data and validated_data['date_of_birth'] == '':
            validated_data['date_of_birth'] = None
            
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 'phone', 'date_of_birth', 'address', 'profile_picture', 'created_at')
        read_only_fields = ('id', 'created_at')

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'date_of_birth', 'address', 'profile_picture')
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
