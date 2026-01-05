"""
GraphQL Types cho Store Module
"""
import graphene
from graphene_django import DjangoObjectType
from store.models import Store, StoreUser, AddressStore


class StoreType(DjangoObjectType):
    """GraphQL Type cho Store"""
    full_address = graphene.String()
    avatar = graphene.String()
    cover_image = graphene.String()
    logo = graphene.String()
    
    class Meta:
        model = Store
        fields = "__all__"
    
    def resolve_full_address(self, info):
        """Lấy địa chỉ mặc định đầy đủ"""
        default_address = self.addresses.filter(is_default=True).first()
        return default_address.full_address if default_address else ""
    def resolve_avatar(self, info):
        """Trả về URL đầy đủ của avatar"""
        if self.avatar:
            print("Avatar URL:", self.avatar.url)
            return info.context.build_absolute_uri(self.avatar.url)
        return ""
    def resolve_cover_image(self, info):
        """Trả về URL đầy đủ của cover image"""
        if self.cover_image:
            print("Cover Image URL:", self.cover_image.url)
            return info.context.build_absolute_uri(self.cover_image.url)
        return ""

    def resolve_logo(self, info):
        """Trả về URL đầy đủ của logo"""
        if self.logo:
            return info.context.build_absolute_uri(self.logo.url)
        return ""
    
class StoreUserType(DjangoObjectType):
    """GraphQL Type cho StoreUser - Quản lý thành viên cửa hàng"""
    class Meta:
        model = StoreUser
        fields = "__all__"


class AddressStoreType(DjangoObjectType):
    """GraphQL Type cho AddressStore - Quản lý địa chỉ cửa hàng"""
    full_address = graphene.String()
    
    class Meta:
        model = AddressStore
        fields = "__all__"
    
    def resolve_full_address(self, info):
        """Trả về địa chỉ đầy đủ"""
        return self.full_address
