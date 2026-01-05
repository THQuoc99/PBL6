"""
SHOEX GraphQL API Schema
Hiện tại chỉ phát triển User module để test và kiểm tra
"""

import graphene
from django.conf import settings

# Import từ user app
from .user.schema import UserQuery, UserMutation
from .product.schema import ProductQuery, ProductMutation
from .brand.schema import BrandQuery, BrandMutations
from .store.schema import StoreQuery, StoreMutation
from .cart.schema import CartQueries, CartMutations
from .address.schema import AddressQueries,AddressMutations
from .discount.schema import VoucherQuery,VoucherMutations
from .shipment.schema import ShipmentQuery
from .order.schema import OrderMutations, OrderQueries
from .payment.schema import PaymentMutations
from .settlements.schema import SettlementMutation,SettlementQuery
# Import từ các apps khác khi cần phát triển
# from .orders.schema import OrderQueries, OrderMutations
# from .payments.schema import PaymentMutations
# from .reviews.schema import ReviewQueries, ReviewMutations
# from .shipments.schema import ShipmentQueries, ShipmentMutations
# from .chatbot.schema import ChatbotQueries, ChatbotMutations



# Import dashboard
from .dashboard.schema import DashboardQuery, DashboardMutation

class Query(
    UserQuery,
    ProductQuery,
    BrandQuery,
    StoreQuery,
    CartQueries,
    AddressQueries,
    VoucherQuery,
    ShipmentQuery,
    OrderQueries,
    SettlementQuery,
    DashboardQuery,
    # OrderQueries, 
    # ReviewQueries,
    # ShipmentQueries,
    # ChatbotQueries,
    graphene.ObjectType
):
    """
    Root Query cho SHOEX GraphQL API
    Hiện tại chỉ có User queries
    """
    
    # Root field cho health check
    health = graphene.String(description="Health check endpoint")
    
    def resolve_health(self, info):
        """Simple health check"""
        return "SHOEX GraphQL API is running! (User module only)"


class Mutation(
    UserMutation,
    ProductMutation,
    BrandMutations,
    StoreMutation,
    CartMutations,
    AddressMutations,
    VoucherMutations,
    OrderMutations,
    PaymentMutations,
    SettlementMutation,
    DashboardMutation,
    # OrderMutations,
    # PaymentMutations, 
    # ReviewMutations,
    # ShipmentMutations,
    # ChatbotMutations,
    graphene.ObjectType
):
    """
    Root Mutation cho SHOEX GraphQL API
    Hiện tại chỉ có User mutations
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

