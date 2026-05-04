import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Appointment

User = get_user_model()

class AppointmentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.appointment_id = self.scope['url_route']['kwargs']['appointment_id']
        self.appointment_group_name = f'appointment_{self.appointment_id}'
        
        # Join appointment group
        await self.channel_layer.group_add(
            self.appointment_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave appointment group
        await self.channel_layer.group_discard(
            self.appointment_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')
        message = text_data_json.get('message', '')
        
        # Send message to appointment group
        await self.channel_layer.group_send(
            self.appointment_group_name,
            {
                'type': 'appointment_message',
                'message_type': message_type,
                'message': message,
                'username': self.scope["user"].username if self.scope["user"].is_authenticated else 'Anonymous'
            }
        )
    
    # Receive message from appointment group
    async def appointment_message(self, event):
        message_type = event['message_type']
        message = event['message']
        username = event['username']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': message_type,
            'message': message,
            'username': username
        }))
    
    @database_sync_to_async
    def get_appointment(self):
        return Appointment.objects.get(id=self.appointment_id)
