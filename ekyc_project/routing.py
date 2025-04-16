from django.urls import re_path
from ekyc.consumers import NLPConsumer

websocket_urlpatterns = [
    re_path(r'ws/nlp/$', NLPConsumer.as_asgi()),  # Simplified pattern
]
