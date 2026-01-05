# graphql_api/store/schema.py
"""
Store GraphQL Schema - Query và Mutation cho Store Module
"""
import graphene
from graphene import ID, List, Field, String

from store.models import Store, StoreUser, AddressStore

# Import types
from .types.types import StoreType, StoreUserType, AddressStoreType

# Import mutations
from .mutations.mutations import (
    CreateStore, UpdateStore, UpdateStoreImages,
    CreateAddressStore, UpdateAddressStore, DeleteAddressStore, SetDefaultAddress,
    CreateStoreUser, UpdateStoreUser, DeleteStoreUser,
)

# Import dashboard query
from .queries.dashboard import StoreDashboardQuery
from .queries.admin_analytics import AdminAnalyticsQuery



# ===================================================================
# ============================ QUERY ================================
# ===================================================================

class StoreQuery(StoreDashboardQuery, AdminAnalyticsQuery, graphene.ObjectType):
    # Store
    store = graphene.Field(StoreType, store_id=ID(required=True))
    stores = List(StoreType)

    # Query MỚI: Lấy cửa hàng mà user là owner (chỉ 1 cái)
    my_owned_store = graphene.Field(
        StoreType,
        description="Lấy cửa hàng duy nhất mà user đang đăng nhập là owner"
    )

    # Query: lấy cửa hàng theo user_id (dùng để admin/view-as)
    my_owned_store_by_user = graphene.Field(
        StoreType,
        user_id=ID(required=True),
        description="Lấy cửa hàng duy nhất theo user id (user là owner)"
    )

    # Address Store
    address_store = graphene.Field(AddressStoreType, address_id=ID(required=True))
    address_stores = List(AddressStoreType, store_id=String(required=False))

    # Store User
    store_user = graphene.Field(StoreUserType, store_user_id=ID(required=True))
    store_users = List(StoreUserType, store_id=String(required=False), user_id=String(required=False))

    # ==================== RESOLVERS ====================

    def resolve_store(self, info, store_id):
        try:
            return Store.objects.get(store_id=store_id)
        except Store.DoesNotExist:
            return None

    def resolve_stores(self, info):
        return Store.objects.all().order_by('-created_at')

    # Resolver cho my_owned_store
    def resolve_my_owned_store(self, info):
        # Lấy user từ context (đã được authenticate bởi JWT middleware)
        user = info.context.user
        print('Resolving my_owned_store for user:', user    )
        if not user or not user.is_authenticated:
            return None

        membership = StoreUser.objects.filter(
            user=user,
            role__in=['owner', 'admin'],
            status='active'
        ).select_related('store').first()
        print('Membership found for user:', membership)
        return membership.store if membership else None

    def resolve_my_owned_store_by_user(self, info, user_id):
        # Find the active store membership for the given user id
        try:
            membership = StoreUser.objects.filter(
                user__id=user_id,
                status='active'
            ).select_related('store').first()
            return membership.store if membership else None
        except Exception:
            return None

    # Address
    def resolve_address_store(self, info, address_id):
        try:
            return AddressStore.objects.get(address_id=address_id)
        except AddressStore.DoesNotExist:
            return None

    def resolve_address_stores(self, info, store_id=None):
        qs = AddressStore.objects.all()
        if store_id:
            qs = qs.filter(store__store_id=store_id)
        return qs.order_by('-is_default', 'address_id')

    # StoreUser
    def resolve_store_user(self, info, store_user_id):
        try:
            return StoreUser.objects.get(id=store_user_id)
        except StoreUser.DoesNotExist:
            return None

    def resolve_store_users(self, info, store_id=None, user_id=None):
        qs = StoreUser.objects.all()
        if store_id:
            qs = qs.filter(store__store_id=store_id)
        if user_id:
            qs = qs.filter(user__id=user_id)
        return qs.order_by('-created_at')



# ===================================================================
# ========================== ALL MUTATIONS ==========================
# ===================================================================

class StoreMutation(graphene.ObjectType):
    create_store = CreateStore.Field()
    update_store = UpdateStore.Field()
    update_store_images = UpdateStoreImages.Field()

    create_address_store = CreateAddressStore.Field()
    update_address_store = UpdateAddressStore.Field()
    delete_address_store = DeleteAddressStore.Field()
    set_default_address = SetDefaultAddress.Field()

    create_store_user = CreateStoreUser.Field()
    update_store_user = UpdateStoreUser.Field()
    delete_store_user = DeleteStoreUser.Field()