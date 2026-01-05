from django.contrib import admin
from django.urls import path, include
from graphene_file_upload.django import FileUploadGraphQLView
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from graphql_api.api import schema

def home_view(request):
    return HttpResponse("""
    <h1>SHOEX API Server</h1>
    <p>Server đang chạy thành công!</p>
    <p><a href="/graphql/">GraphQL Playground</a></p>
    <p><a href="/admin/">Admin</a></p>
    """)

urlpatterns = [
    path('', home_view, name='home'),

    # Django admin
    path('admin/', admin.site.urls),

    # GraphQL
    path(
        'graphql/',
        csrf_exempt(
            FileUploadGraphQLView.as_view(graphiql=True, schema=schema)
        )
    ),

    # REST / Webhook APIs
    path('shipments/', include('shipments.urls')),
    path('', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
