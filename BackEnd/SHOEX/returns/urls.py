from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReturnRequestViewSet

router = DefaultRouter()
router.register(r'returns', ReturnRequestViewSet, basename='returns')

urlpatterns = router.urls
