from django.urls import path
from . import views

urlpatterns = [
    # Notification endpoints
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:notification_id>/mark-read/', views.mark_notification_read, name='mark-notification-read'),
    path('<int:notification_id>/mark-unread/', views.mark_notification_unread, name='mark-notification-unread'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('count/', views.notification_count, name='notification-count'),
    
    # Preference endpoints
    path('preferences/', views.NotificationPreferenceView.as_view(), name='notification-preferences'),
    
    # Template endpoints (admin only)
    path('templates/', views.NotificationTemplateListView.as_view(), name='notification-templates'),
    path('create/', views.create_notification, name='create-notification'),
]
