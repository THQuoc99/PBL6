
from django.contrib import admin
from django.urls import path, include
from graphene_file_upload.django import FileUploadGraphQLView  # Thay đổi import
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Import schema đúng cách
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import schema từ graphql app
from graphql_api.api import schema

def home_view(request):
    return HttpResponse("""
    <h1>SHOEX API Server</h1>
    <p>Server đang chạy thành công!</p>
    <p><a href="/graphql/">GraphQL Playground</a></p>
    <p><a href="/admin/">Admin</a></p>
    """)

urlpatterns = [
    path('', home_view, name='home'),  # Root URL
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True, schema=schema))),  # Sử dụng FileUploadGraphQLView
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)