from django.urls import path
from . import views

urlpatterns = [
    # Doctor profile endpoints
    path('', views.DoctorProfileListView.as_view(), name='doctor-list'),
    path('specializations/', views.doctor_specializations, name='doctor-specializations'),
    path('<int:pk>/', views.DoctorProfileDetailView.as_view(), name='doctor-detail'),
    path('<int:doctor_id>/available-slots/', views.doctor_available_slots, name='doctor-available-slots'),
    path('create/', views.DoctorProfileCreateView.as_view(), name='doctor-create'),
    path('<int:pk>/update/', views.DoctorProfileUpdateView.as_view(), name='doctor-update'),
    path('my-profile/', views.my_doctor_profile, name='my-doctor-profile'),
    
    # Time slot endpoints
    path('<int:doctor_id>/time-slots/', views.TimeSlotListCreateView.as_view(), name='doctor-time-slots'),
    path('<int:doctor_id>/time-slots/<int:slot_id>/', views.TimeSlotDetailView.as_view(), name='doctor-time-slot-detail'),
    
    # Review endpoints
    path('<int:doctor_id>/reviews/', views.DoctorReviewListCreateView.as_view(), name='doctor-reviews'),
]
