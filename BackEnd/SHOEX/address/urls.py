from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProvinceListView, WardListView, HamletListView, UserAddressViewSet

router = DefaultRouter()
router.register(r'my-addresses', UserAddressViewSet, basename='user-address')

urlpatterns = [
    path('provinces/', ProvinceListView.as_view()),
    path('wards/', WardListView.as_view()),
    path('hamlets/', HamletListView.as_view()),
    path('', include(router.urls)),
]