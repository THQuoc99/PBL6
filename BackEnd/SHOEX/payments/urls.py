# ...existing code...
from django.urls import path
from .vnpayIPN import vnpay_ipn
from . import views
urlpatterns = [
    path('api/payment/vnpay/ipn', vnpay_ipn, name='vnpay_ipn'),
    path('api/vnpay/verify-return', views.verify_return, name='vnpay_verify_return'),
    path('api/vnpay/verify-return-store', views.verify_return_store, name='vnpay_verify_return_store'),
    # ...other payment urls...
]
# ...existing code...