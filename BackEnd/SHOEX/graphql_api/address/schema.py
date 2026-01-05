
import graphene
from graphene import relay
from .types import AddressType
from address.models import Address
from .mutations.mutations import (
    AddAddressMutation,
    UpdateAddressMutation,
    DeleteAddressMutation,
    SetDefaultAddressMutation
)


class AddressQueries(graphene.ObjectType):
    """Address queries"""
    
    # Lấy tất cả địa chỉ của user
    my_addresses = graphene.List(
        AddressType,
        description="Lấy danh sách địa chỉ của người dùng hiện tại"
    )
    
    # Lấy địa chỉ mặc định
    my_default_address = graphene.Field(
        AddressType,
        description="Lấy địa chỉ mặc định của người dùng"
    )
    
    # Lấy địa chỉ theo ID
    address = graphene.Field(
        AddressType,
        address_id=graphene.Int(required=True),
        description="Lấy địa chỉ theo ID"
    )
    
    def resolve_my_addresses(self, info):
        """Lấy tất cả địa chỉ của user"""
        user = info.context.user
        
        if not user or not user.is_authenticated:
            return []
        
        return Address.objects.filter(user=user).order_by('-is_default', 'address_id')
    
    def resolve_my_default_address(self, info):
        """Lấy địa chỉ mặc định"""
        user = info.context.user
        
        if not user or not user.is_authenticated:
            return None
        
        return Address.objects.filter(user=user, is_default=True).first()
    
    def resolve_address(self, info, address_id):
        """Lấy địa chỉ theo ID"""
        user = info.context.user
        
        if not user or not user.is_authenticated:
            return None
        
        try:
            return Address.objects.get(address_id=address_id, user=user)
        except Address.DoesNotExist:
            return None


class AddressMutations(graphene.ObjectType):
    """Address mutations"""
    
    add_address = AddAddressMutation.Field(description="Thêm địa chỉ mới")
    update_address = UpdateAddressMutation.Field(description="Cập nhật địa chỉ")
    delete_address = DeleteAddressMutation.Field(description="Xóa địa chỉ")
    set_default_address = SetDefaultAddressMutation.Field(description="Đặt địa chỉ làm mặc định")
