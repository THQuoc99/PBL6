from django.urls import path
from .views import OrderViewSet

order_list = OrderViewSet.as_view({'get': 'list'})
create_order = OrderViewSet.as_view({'post': 'create_order'})
cancel_order = OrderViewSet.as_view({'post': 'cancel'})
confirm_order = OrderViewSet.as_view({'post': 'confirm'})

urlpatterns = [
    path('create/', create_order, name='create-order'),
    path('', order_list, name='order-list'),
    path('<int:pk>/cancel/', cancel_order, name='cancel-order'),
    path('<int:pk>/confirm/', confirm_order, name='confirm-order'),
]