
from django.contrib import admin
from django.urls import include, path
from graphene_django.views import GraphQLView
from graphql_api.api import schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
    path('payments/', include('payments.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('api/users/', include('users.urls')),

]
