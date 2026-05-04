import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_project.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Create or update admin user
try:
    admin = User.objects.get(email='admin@medical.com')
    admin.is_staff = True
    admin.is_superuser = True
    admin.set_password('password123')
    admin.save()
    print("Admin user updated successfully!")
except User.DoesNotExist:
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@medical.com',
        password='password123',
        first_name='Admin',
        last_name='User'
    )
    print("Admin user created successfully!")

print("Login credentials:")
print("Email: admin@medical.com")
print("Password: password123")
