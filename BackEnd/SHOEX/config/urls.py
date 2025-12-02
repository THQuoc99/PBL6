from django.contrib import admin
from django.urls import include, path
from graphene_django.views import GraphQLView
from graphql_api.api import schema
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
    
    # --- CÁC APP CŨ ---
    path('payments/', include('payments.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('api/users/', include('users.urls')),
    path('api/', include('products.urls')), 
    path('api/address/', include('address.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/orders/', include('orders.urls')),

    # --- CÁC APP MỚI CẦN BỔ SUNG (Để khớp với datanew.sql) ---
    path('api/store/', include('store.urls')),       # Quan trọng: Quản lý cửa hàng
    path('api/reviews/', include('reviews.urls')),   # Đánh giá sản phẩm
    path('api/shipments/', include('shipments.urls')), # Theo dõi vận chuyển
    path('api/discounts/', include('discount.urls')),  # Quản lý Voucher
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)