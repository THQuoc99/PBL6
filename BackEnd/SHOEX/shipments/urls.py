from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShipmentViewSet, ghtk_webhook

router = DefaultRouter()
router.register(r'', ShipmentViewSet, basename='shipment')

urlpatterns = [
    path('', include(router.urls)),
    path('ghtk-webhook/', ghtk_webhook, name='ghtk-webhook'),  # Webhook endpoint
]