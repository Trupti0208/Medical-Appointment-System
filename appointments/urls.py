from django.urls import path
from . import views

urlpatterns = [
    # Appointment endpoints
    path('', views.AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment, name='appointment-cancel'),
    path('<int:appointment_id>/reschedule/', views.reschedule_appointment, name='appointment-reschedule'),
    path('my-appointments/', views.my_appointments, name='my-appointments'),
    path('dashboard/', views.appointment_dashboard, name='appointment-dashboard'),
    
    # Reschedule request endpoints
    path('reschedule-requests/', views.AppointmentRescheduleListView.as_view(), name='reschedule-requests'),
    path('reschedule-requests/<int:reschedule_id>/approve/', views.approve_reschedule, name='approve-reschedule'),
    path('reschedule-requests/<int:reschedule_id>/reject/', views.reject_reschedule, name='reject-reschedule'),
    
    # Medical record endpoints
    path('medical-records/', views.MedicalRecordListCreateView.as_view(), name='medical-records'),
    
    # Review endpoints
    path('reviews/', views.AppointmentReviewListCreateView.as_view(), name='appointment-reviews'),
]
