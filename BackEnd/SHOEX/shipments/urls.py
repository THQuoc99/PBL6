# shipping/urls.py
from django.urls import path
from .webhooks import ghtk_webhook

urlpatterns = [
    path('webhook/ghtk/', ghtk_webhook, name='ghtk_webhook'),
]
