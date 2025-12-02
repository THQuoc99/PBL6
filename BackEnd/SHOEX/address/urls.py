from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserAddressViewSet

router = DefaultRouter()
router.register(r'my-addresses', UserAddressViewSet, basename='user-address')

urlpatterns = [
    path('', include(router.urls)),
]