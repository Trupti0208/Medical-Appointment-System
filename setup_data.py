import os
import django
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_project.settings')
django.setup()

User = get_user_model()

def create_sample_data():
    print("Creating sample data...")
    
    # Create sample users
    users_data = [
        {
            'username': 'john_patient',
            'email': 'john.patient@email.com',
            'first_name': 'John',
            'last_name': 'Patient',
            'role': 'PATIENT',
        },
        {
            'username': 'jane_patient',
            'email': 'jane.patient@email.com',
            'first_name': 'Jane',
            'last_name': 'Patient',
            'role': 'PATIENT',
        },
        {
            'username': 'bob_doctor',
            'email': 'bob.doctor@medical.com',
            'first_name': 'Bob',
            'last_name': 'Smith',
            'role': 'DOCTOR',
        },
        {
            'username': 'alice_doctor',
            'email': 'alice.doctor@medical.com',
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'role': 'DOCTOR',
        },
    ]

    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"Created user: {user.email}")

    # Create doctor profiles
    from doctors.models import DoctorProfile, TimeSlot
    
    doctors_data = [
        {
            'user_email': 'bob.doctor@medical.com',
            'name': 'Dr. Bob Smith',
            'specialization': 'Cardiology',
            'qualifications': 'MD, FACC',
            'experience_years': 15,
            'license_number': 'DOC001',
            'clinic_name': 'Heart Care Center',
            'clinic_address': '123 Medical St, City, State',
            'consultation_fee': 150.00,
            'bio': 'Experienced cardiologist specializing in heart diseases and conditions.',
        },
        {
            'user_email': 'alice.doctor@medical.com',
            'name': 'Dr. Alice Johnson',
            'specialization': 'Pediatrics',
            'qualifications': 'MD, FAAP',
            'experience_years': 10,
            'license_number': 'DOC002',
            'clinic_name': 'Kids Health Clinic',
            'clinic_address': '456 Child Ave, City, State',
            'consultation_fee': 120.00,
            'bio': 'Dedicated pediatrician with expertise in child healthcare and development.',
        },
    ]

    for doctor_data in doctors_data:
        user = User.objects.get(email=doctor_data['user_email'])
        # Remove user_email from doctor_data as it's not a field in DoctorProfile
        profile_data = {k: v for k, v in doctor_data.items() if k != 'user_email'}
        profile, created = DoctorProfile.objects.get_or_create(
            user=user,
            defaults=profile_data
        )
        if created:
            print(f"Created doctor profile: {profile.name}")
            # Create time slots
            create_time_slots_for_doctor(profile)

    print("Sample data created successfully!")

def create_time_slots_for_doctor(doctor):
    """Create time slots for a doctor"""
    from doctors.models import TimeSlot
    time_slots = [
        {'day_of_week': 0, 'start_time': '09:00', 'end_time': '09:30'},  # Monday
        {'day_of_week': 0, 'start_time': '09:30', 'end_time': '10:00'},
        {'day_of_week': 0, 'start_time': '10:00', 'end_time': '10:30'},
        {'day_of_week': 0, 'start_time': '10:30', 'end_time': '11:00'},
        {'day_of_week': 0, 'start_time': '14:00', 'end_time': '14:30'},
        {'day_of_week': 0, 'start_time': '14:30', 'end_time': '15:00'},
        {'day_of_week': 0, 'start_time': '15:00', 'end_time': '15:30'},
        {'day_of_week': 0, 'start_time': '15:30', 'end_time': '16:00'},
        
        {'day_of_week': 1, 'start_time': '09:00', 'end_time': '09:30'},  # Tuesday
        {'day_of_week': 1, 'start_time': '09:30', 'end_time': '10:00'},
        {'day_of_week': 1, 'start_time': '10:00', 'end_time': '10:30'},
        {'day_of_week': 1, 'start_time': '10:30', 'end_time': '11:00'},
        {'day_of_week': 1, 'start_time': '14:00', 'end_time': '14:30'},
        {'day_of_week': 1, 'start_time': '14:30', 'end_time': '15:00'},
        {'day_of_week': 1, 'start_time': '15:00', 'end_time': '15:30'},
        {'day_of_week': 1, 'start_time': '15:30', 'end_time': '16:00'},
        
        {'day_of_week': 2, 'start_time': '09:00', 'end_time': '09:30'},  # Wednesday
        {'day_of_week': 2, 'start_time': '09:30', 'end_time': '10:00'},
        {'day_of_week': 2, 'start_time': '10:00', 'end_time': '10:30'},
        {'day_of_week': 2, 'start_time': '10:30', 'end_time': '11:00'},
        {'day_of_week': 2, 'start_time': '14:00', 'end_time': '14:30'},
        {'day_of_week': 2, 'start_time': '14:30', 'end_time': '15:00'},
        {'day_of_week': 2, 'start_time': '15:00', 'end_time': '15:30'},
        {'day_of_week': 2, 'start_time': '15:30', 'end_time': '16:00'},
        
        {'day_of_week': 3, 'start_time': '09:00', 'end_time': '09:30'},  # Thursday
        {'day_of_week': 3, 'start_time': '09:30', 'end_time': '10:00'},
        {'day_of_week': 3, 'start_time': '10:00', 'end_time': '10:30'},
        {'day_of_week': 3, 'start_time': '10:30', 'end_time': '11:00'},
        {'day_of_week': 3, 'start_time': '14:00', 'end_time': '14:30'},
        {'day_of_week': 3, 'start_time': '14:30', 'end_time': '15:00'},
        {'day_of_week': 3, 'start_time': '15:00', 'end_time': '15:30'},
        {'day_of_week': 3, 'start_time': '15:30', 'end_time': '16:00'},
        
        {'day_of_week': 4, 'start_time': '09:00', 'end_time': '09:30'},  # Friday
        {'day_of_week': 4, 'start_time': '09:30', 'end_time': '10:00'},
        {'day_of_week': 4, 'start_time': '10:00', 'end_time': '10:30'},
        {'day_of_week': 4, 'start_time': '10:30', 'end_time': '11:00'},
        {'day_of_week': 4, 'start_time': '14:00', 'end_time': '14:30'},
        {'day_of_week': 4, 'start_time': '14:30', 'end_time': '15:00'},
        {'day_of_week': 4, 'start_time': '15:00', 'end_time': '15:30'},
        {'day_of_week': 4, 'start_time': '15:30', 'end_time': '16:00'},
    ]

    for slot_data in time_slots:
        TimeSlot.objects.get_or_create(
            doctor=doctor,
            defaults=slot_data
        )

if __name__ == '__main__':
    create_sample_data()
