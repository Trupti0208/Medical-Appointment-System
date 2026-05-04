import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_project.settings')
django.setup()

from doctors.models import DoctorProfile

# Test if doctors exist
doctors = DoctorProfile.objects.filter(is_available=True)
print(f"Found {doctors.count()} available doctors:")
for doctor in doctors:
    print(f"- {doctor.name} ({doctor.specialization})")

print("\nAPI URLs to test:")
print("1. Django Admin: http://127.0.0.1:8000/admin/")
print("2. Doctors API: http://127.0.0.1:8000/api/doctors/")
print("3. API Root: http://127.0.0.1:8000/api/")
