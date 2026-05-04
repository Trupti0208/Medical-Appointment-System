# Temporarily disabled to avoid conflicts during setup
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth import get_user_model
# from doctors.models import DoctorProfile

# User = get_user_model()

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     """
#     Create a DoctorProfile when a new user with DOCTOR role is created
#     """
#     if created and instance.role == 'DOCTOR':
#         DoctorProfile.objects.create(
#             user=instance,
#             name=instance.full_name,
#             email=instance.email,
#             phone=instance.phone or ''
#         )
