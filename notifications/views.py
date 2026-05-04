from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import Notification, NotificationPreference, NotificationTemplate
from .serializers import (
    NotificationSerializer, NotificationCreateSerializer,
    NotificationPreferenceSerializer, NotificationTemplateSerializer
)

User = get_user_model()

class NotificationListView(generics.ListAPIView):
    """API endpoint for listing user notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notification_type', 'is_read', 'priority']
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related(
            'related_appointment', 'related_doctor', 'related_patient'
        ).order_by('-created_at')

class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving, updating, and deleting notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related(
            'related_appointment', 'related_doctor', 'related_patient'
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """API endpoint for marking notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        serializer = NotificationSerializer(notification)
        return Response({
            'message': 'Notification marked as read',
            'notification': serializer.data
        })
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_unread(request, notification_id):
    """API endpoint for marking notification as unread"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_unread()
        serializer = NotificationSerializer(notification)
        return Response({
            'message': 'Notification marked as unread',
            'notification': serializer.data
        })
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """API endpoint for marking all notifications as read"""
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
    count = unread_notifications.count()
    unread_notifications.update(is_read=True)
    
    return Response({
        'message': f'Marked {count} notifications as read'
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_count(request):
    """API endpoint for getting notification counts"""
    user = request.user
    
    total_notifications = Notification.objects.filter(user=user).count()
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
    important_notifications = Notification.objects.filter(
        user=user, 
        is_important=True, 
        is_read=False
    ).count()
    
    return Response({
        'total': total_notifications,
        'unread': unread_notifications,
        'important': important_notifications
    })

class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """API endpoint for viewing and updating notification preferences"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preference, created = NotificationPreference.objects.get_or_create(user=self.request.user)
        return preference

class NotificationTemplateListView(generics.ListAPIView):
    """API endpoint for listing notification templates (admin only)"""
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return NotificationTemplate.objects.all()
        return NotificationTemplate.objects.none()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_notification(request):
    """API endpoint for creating notifications (admin only)"""
    if request.user.role != 'ADMIN':
        return Response({'error': 'Only admins can create notifications'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = NotificationCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    notification = serializer.save()
    
    return Response({
        'message': 'Notification created successfully',
        'notification': NotificationSerializer(notification).data
    }, status=status.HTTP_201_CREATED)
