from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

from doctors.models import DoctorProfile, TimeSlot
from appointments.models import Appointment
from notifications.models import NotificationTemplate

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for the medical appointment system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create notification templates
        self.create_notification_templates()
        
        # Create sample users
        self.create_sample_users()
        
        # Create sample doctors
        self.create_sample_doctors()
        
        # Create sample appointments
        self.create_sample_appointments()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def create_notification_templates(self):
        """Create notification templates"""
        templates = [
            {
                'notification_type': 'APPOINTMENT_BOOKED',
                'title_template': 'Appointment Booked Successfully',
                'message_template': 'Your appointment with Dr. {doctor_name} on {appointment_date} at {appointment_time} has been booked.',
                'action_text_template': 'View Appointment',
                'default_priority': 'HIGH',
                'default_is_important': True,
            },
            {
                'notification_type': 'APPOINTMENT_CANCELLED',
                'title_template': 'Appointment Cancelled',
                'message_template': 'Your appointment with Dr. {doctor_name} on {appointment_date} has been cancelled.',
                'default_priority': 'MEDIUM',
                'default_is_important': False,
            },
            {
                'notification_type': 'APPOINTMENT_CONFIRMED',
                'title_template': 'Appointment Confirmed',
                'message_template': 'Your appointment with Dr. {doctor_name} on {appointment_date} at {appointment_time} has been confirmed.',
                'default_priority': 'HIGH',
                'default_is_important': True,
            },
            {
                'notification_type': 'APPOINTMENT_RESCHEDULED',
                'title_template': 'Appointment Reschedule Request',
                'message_template': 'Your appointment has been rescheduled from {old_date} to {new_date}.',
                'default_priority': 'MEDIUM',
                'default_is_important': False,
            },
        ]

        for template_data in templates:
            NotificationTemplate.objects.get_or_create(
                notification_type=template_data['notification_type'],
                defaults=template_data
            )

    def create_sample_users(self):
        """Create sample users"""
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@medical.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            },
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
                defaults={
                    **user_data,
                    'password': 'password123',  # Simple password for testing
                }
            )
            if created:
                user.set_password('password123')
                user.save()

    def create_sample_doctors(self):
        """Create sample doctor profiles"""
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
            profile, created = DoctorProfile.objects.get_or_create(
                user=user,
                defaults=doctor_data
            )
            
            # Create time slots for each doctor
            if created:
                self.create_time_slots_for_doctor(profile)

    def create_time_slots_for_doctor(self, doctor):
        """Create time slots for a doctor"""
        time_slots = [
            {'day_of_week': 0, 'start_time': '09:00', 'end_time': '09:30'},  # Monday
            {'day_of_week': 0, 'start_time': '09:30', 'end_time': '10:00'},
            {'day_of_week': 0, 'start_time': '10:00', 'end_time': '10:30'},
            {'day_of_week': 0, 'start_time': '10:30', 'end_time': '11:00'},
            {'day_of_week': 0, 'start_time': '11:00', 'end_time': '11:30'},
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

    def create_sample_appointments(self):
        """Create sample appointments"""
        patient1 = User.objects.get(email='john.patient@email.com')
        patient2 = User.objects.get(email='jane.patient@email.com')
        doctor1 = DoctorProfile.objects.get(user__email='bob.doctor@medical.com')
        doctor2 = DoctorProfile.objects.get(user__email='alice.doctor@medical.com')

        appointments_data = [
            {
                'patient': patient1,
                'doctor': doctor1,
                'appointment_date': timezone.now().date() + timedelta(days=2),
                'time_slot': doctor1.time_slots.first(),
                'status': 'SCHEDULED',
                'reason_for_visit': 'Regular checkup and heart monitoring',
                'symptoms': 'Occasional chest pain',
                'consultation_fee': doctor1.consultation_fee,
            },
            {
                'patient': patient2,
                'doctor': doctor2,
                'appointment_date': timezone.now().date() + timedelta(days=3),
                'time_slot': doctor2.time_slots.first(),
                'status': 'CONFIRMED',
                'reason_for_visit': 'Child vaccination and general checkup',
                'symptoms': 'Fever and cough',
                'consultation_fee': doctor2.consultation_fee,
            },
        ]

        for appointment_data in appointments_data:
            Appointment.objects.get_or_create(
                patient=appointment_data['patient'],
                doctor=appointment_data['doctor'],
                appointment_date=appointment_data['appointment_date'],
                time_slot=appointment_data['time_slot'],
                defaults=appointment_data
            )
