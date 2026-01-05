"""
GraphQL Input Types cho Store Module
"""
import graphene
from graphene import InputObjectType


class StoreCreateInput(InputObjectType):
    """Input để tạo Store mới"""
    name = graphene.String(required=True)
    email = graphene.String()
    description = graphene.String()
    # Support multiple addresses on create
    addresses = graphene.List(lambda: AddressStoreInput)

class AddressStoreInput(InputObjectType):
    """Input để tạo/cập nhật AddressStore"""
    address_id = graphene.ID(required=False)
    province = graphene.String(required=True)
    ward = graphene.String(required=True)
    hamlet = graphene.String()
    detail = graphene.String(required=True)
    is_default = graphene.Boolean()
    phone = graphene.String()


class StoreUserInput(InputObjectType):
    """Input để tạo/cập nhật StoreUser"""
    store_id = graphene.String(required=True)
    role = graphene.String(required=True)
    status = graphene.String()
    granted_permissions = graphene.JSONString()
    revoked_permissions = graphene.JSONString()
    notes = graphene.String()
