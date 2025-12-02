from django.urls import path
from .views import OrderViewSet

order_list = OrderViewSet.as_view({'get': 'list'})
create_order = OrderViewSet.as_view({'post': 'create_order'})

urlpatterns = [
    path('create/', OrderViewSet.as_view({'post': 'create_order'}), name='create-order'),
    path('', order_list, name='order-list'),
]