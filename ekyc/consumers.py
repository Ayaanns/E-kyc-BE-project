from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

class NLPConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "nlp_group"
        # Join nlp group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()
        print("WebSocket connected")

    def disconnect(self, close_code):
        # Leave nlp group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected with code: {close_code}")

    def receive(self, text_data):
        # Handle received data if needed
        print(f"Received message: {text_data}")

    def nlp_message(self, event):
        # Send message to WebSocket
        try:
            self.send(text_data=json.dumps({
                'type': 'nlp_message',
                'message': event['message']
            }))
            print(f"Message sent to client: {event['message']}")
        except Exception as e:
            print(f"Error sending message: {str(e)}")
