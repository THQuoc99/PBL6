import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q

from address.models import Province, Ward, Hamlet, Address


class ProvinceType(DjangoObjectType):
    """GraphQL type cho Province"""
    
    class Meta:
        model = Province
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
    
    # Thêm các field tùy chỉnh
    total_wards = graphene.Int(description="Tổng số phường/xã trong tỉnh")
    total_addresses = graphene.Int(description="Tổng số địa chỉ trong tỉnh")
    
    def resolve_total_wards(self, info):
        return self.wards.count()
    
    def resolve_total_addresses(self, info):
        return self.addresses.count()


class WardType(DjangoObjectType):
    """GraphQL type cho Ward"""
    
    class Meta:
        model = Ward
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
    
    # Thêm các field tùy chỉnh
    total_hamlets = graphene.Int(description="Tổng số thôn/xóm trong phường/xã")
    total_addresses = graphene.Int(description="Tổng số địa chỉ trong phường/xã")
    full_name = graphene.String(description="Tên đầy đủ: Phường/Xã, Tỉnh")
    
    def resolve_total_hamlets(self, info):
        return self.hamlets.count()
    
    def resolve_total_addresses(self, info):
        return self.addresses.count()
    
    def resolve_full_name(self, info):
        return f"{self.name}, {self.province.name}"


class HamletType(DjangoObjectType):
    """GraphQL type cho Hamlet"""
    
    class Meta:
        model = Hamlet
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
    
    # Thêm các field tùy chỉnh
    total_addresses = graphene.Int(description="Tổng số địa chỉ trong thôn/xóm")
    full_name = graphene.String(description="Tên đầy đủ: Thôn/Xóm, Phường/Xã, Tỉnh")
    
    def resolve_total_addresses(self, info):
        return self.addresses.count()
    
    def resolve_full_name(self, info):
        return f"{self.name}, {self.ward.name}, {self.ward.province.name}"


class AddressType(DjangoObjectType):
    """GraphQL type cho Address"""
    
    class Meta:
        model = Address
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
    
    # Thêm các field tùy chỉnh
    full_address = graphene.String(description="Địa chỉ đầy đủ")
    
    def resolve_full_address(self, info):
        return self.full_address


# Input types cho mutations
class ProvinceInput(graphene.InputObjectType):
    """Input type để tạo/sửa Province"""
    name = graphene.String(required=True, description="Tên tỉnh/thành phố")


class WardInput(graphene.InputObjectType):
    """Input type để tạo/sửa Ward"""
    province_id = graphene.ID(required=True, description="ID của tỉnh/thành phố")
    name = graphene.String(required=True, description="Tên phường/xã")


class HamletInput(graphene.InputObjectType):
    """Input type để tạo/sửa Hamlet"""
    ward_id = graphene.ID(required=True, description="ID của phường/xã")
    name = graphene.String(required=True, description="Tên thôn/xóm")


class AddressInput(graphene.InputObjectType):
    """Input type để tạo/sửa Address"""
    user_id = graphene.ID(required=True, description="ID của người dùng")
    province_id = graphene.ID(required=True, description="ID của tỉnh/thành phố")
    ward_id = graphene.ID(required=True, description="ID của phường/xã")
    hamlet_id = graphene.ID(description="ID của thôn/xóm (tùy chọn)")
    detail = graphene.String(required=True, description="Địa chỉ chi tiết")
    is_default = graphene.Boolean(description="Có phải địa chỉ mặc định không")


# Connection types cho pagination
class ProvinceConnection(graphene.relay.Connection):
    class Meta:
        node = ProvinceType


class WardConnection(graphene.relay.Connection):
    class Meta:
        node = WardType


class HamletConnection(graphene.relay.Connection):
    class Meta:
        node = HamletType


class AddressConnection(graphene.relay.Connection):
    class Meta:
        node = AddressType