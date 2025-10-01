"""
SHOEX GraphQL API Schema
Theo mô hình của Saleor nhưng đơn giản hóa cho dự án SHOEX
"""

import graphene
from django.conf import settings

# Import từ product app
from .product.schema import ProductQueries, ProductMutations

# Import từ user app
from .user.schema import UserQuery, UserMutation

# Import từ các apps khác khi có
# from .orders.schema import OrderQueries, OrderMutations
# from .payments.schema import PaymentMutations
# from .reviews.schema import ReviewQueries, ReviewMutations
# from .shipments.schema import ShipmentQueries, ShipmentMutations
# from .chatbot.schema import ChatbotQueries, ChatbotMutations


class Query(
    ProductQueries,
    UserQuery,
    # OrderQueries, 
    # ReviewQueries,
    # ShipmentQueries,
    # ChatbotQueries,
    graphene.ObjectType
):
    """
    Root Query cho SHOEX GraphQL API
    Tập hợp tất cả queries từ các modules
    """
    
    # Root field cho health check
    health = graphene.String(description="Health check endpoint")
    
    def resolve_health(self, info):
        """Simple health check"""
        return "SHOEX GraphQL API is running!"


class Mutation(
    ProductMutations,
    UserMutation,
    # OrderMutations,
    # PaymentMutations, 
    # ReviewMutations,
    # ShipmentMutations,
    # ChatbotMutations,
    graphene.ObjectType
):
    """
    Root Mutation cho SHOEX GraphQL API
    Tập hợp tất cả mutations từ các modules
    """
    pass


# Create schema với Query và Mutation
schema = graphene.Schema(
    query=Query,
    mutation=Mutation
)


# Additional schema configuration nếu cần
if hasattr(settings, 'GRAPHQL_DEBUG') and settings.GRAPHQL_DEBUG:
    # Enable GraphQL debug mode
    schema.get_type('Query').add_to_class('_debug', graphene.Field(graphene.String))


# Export cho Django urls.py
__all__ = ['schema']


"""
Usage trong urls.py:

from django.urls import path
from graphene_django.views import GraphQLView
from .graphql.api import schema

urlpatterns = [
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
]

Hoặc với authentication:

from django.contrib.auth.decorators import login_required
from graphene_django.views import GraphQLView

urlpatterns = [
    path('graphql/', 
         login_required(GraphQLView.as_view(graphiql=True, schema=schema)),
         name='graphql'),
]
"""
