from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, get_user_wishlist, toggle_wishlist_api

router = DefaultRouter()
router.register(r'', CartViewSet, basename='cart')

urlpatterns = [
    path('wishlist/', get_user_wishlist, name='get_wishlist'),
    path('wishlist/toggle/', toggle_wishlist_api, name='toggle_wishlist'),

    path('', include(router.urls)),
]