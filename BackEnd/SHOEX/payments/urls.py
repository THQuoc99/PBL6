from django.urls import path
from . import views

urlpatterns = [
    path("paypal/<int:order_id>/", views.create_paypal_payment, name="create_paypal_payment"),
    path("paypal-success", views.paypal_success, name="paypal_success"),
    path("paypal-cancel", views.paypal_cancel, name="paypal_cancel"),
    path("vnpay/<int:order_id>/", views.create_vnpay_payment, name="create_vnpay_payment"),
    path("vnpay-return/", views.vnpay_return, name="vnpay_return"),
    path("vnpay-ipn/", views.vnpay_ipn, name="vnpay_ipn"),
    
]
