import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Q

from address.models import Province, Ward, Hamlet, Address
from .types.address import (
    ProvinceType, WardType, HamletType, AddressType,
    ProvinceConnection, WardConnection, HamletConnection, AddressConnection
)
from .mutations.address_mutations import AddressMutation
from .filters.address_filters import (
    ProvinceFilter, WardFilter, HamletFilter, AddressFilter
)
from .dataloaders.address_loaders import get_address_dataloaders


class AddressQuery(graphene.ObjectType):
    """GraphQL Queries cho Address module"""
    
    # Single queries
    province = graphene.Field(
        ProvinceType,
        id=graphene.ID(required=True),
        description="Lấy thông tin một tỉnh/thành phố theo ID"
    )
    
    ward = graphene.Field(
        WardType,
        id=graphene.ID(required=True),
        description="Lấy thông tin một phường/xã theo ID"
    )
    
    hamlet = graphene.Field(
        HamletType,
        id=graphene.ID(required=True),
        description="Lấy thông tin một thôn/xóm theo ID"
    )
    
    address = graphene.Field(
        AddressType,
        id=graphene.ID(required=True),
        description="Lấy thông tin một địa chỉ theo ID"
    )
    
    # List queries with filtering and pagination
    provinces = DjangoFilterConnectionField(
        ProvinceType,
        filterset_class=ProvinceFilter,
        description="Danh sách tỉnh/thành phố với filter và pagination"
    )
    
    wards = DjangoFilterConnectionField(
        WardType,
        filterset_class=WardFilter,
        description="Danh sách phường/xã với filter và pagination"
    )
    
    hamlets = DjangoFilterConnectionField(
        HamletType,
        filterset_class=HamletFilter,
        description="Danh sách thôn/xóm với filter và pagination"
    )
    
    addresses = DjangoFilterConnectionField(
        AddressType,
        filterset_class=AddressFilter,
        description="Danh sách địa chỉ với filter và pagination"
    )
    
    # Simple list queries (không pagination)
    all_provinces = graphene.List(
        ProvinceType,
        description="Lấy danh sách tất cả tỉnh/thành phố (không pagination)"
    )
    
    all_wards = graphene.List(
        WardType,
        province_id=graphene.ID(),
        description="Lấy danh sách tất cả phường/xã (có thể filter theo tỉnh)"
    )
    
    all_hamlets = graphene.List(
        HamletType,
        ward_id=graphene.ID(),
        description="Lấy danh sách tất cả thôn/xóm (có thể filter theo phường/xã)"
    )
    
    # Custom queries
    user_addresses = graphene.List(
        AddressType,
        user_id=graphene.ID(required=True),
        description="Lấy tất cả địa chỉ của một user"
    )
    
    user_default_address = graphene.Field(
        AddressType,
        user_id=graphene.ID(required=True),
        description="Lấy địa chỉ mặc định của user"
    )
    
    wards_by_province = graphene.List(
        WardType,
        province_id=graphene.ID(required=True),
        description="Lấy tất cả phường/xã trong một tỉnh/thành"
    )
    
    hamlets_by_ward = graphene.List(
        HamletType,
        ward_id=graphene.ID(required=True),
        description="Lấy tất cả thôn/xóm trong một phường/xã"
    )
    
    search_addresses = graphene.List(
        AddressType,
        search_term=graphene.String(required=True),
        limit=graphene.Int(default_value=20),
        description="Tìm kiếm địa chỉ theo từ khóa"
    )
    
    # Resolvers cho single queries
    def resolve_province(self, info, id):
        """Resolve province by ID sử dụng dataloader"""
        dataloaders = get_address_dataloaders(info)
        return dataloaders.province_by_id.load(int(id))
    
    def resolve_ward(self, info, id):
        """Resolve ward by ID sử dụng dataloader"""
        dataloaders = get_address_dataloaders(info)
        return dataloaders.ward_by_id.load(int(id))
    
    def resolve_hamlet(self, info, id):
        """Resolve hamlet by ID sử dụng dataloader"""
        dataloaders = get_address_dataloaders(info)
        return dataloaders.hamlet_by_id.load(int(id))
    
    def resolve_address(self, info, id):
        """Resolve address by ID sử dụng dataloader"""
        dataloaders = get_address_dataloaders(info)
        return dataloaders.address_by_id.load(int(id))
    
    # Resolvers cho simple list queries
    def resolve_all_provinces(self, info):
        """Resolve tất cả provinces"""
        return Province.objects.all().order_by('name')
    
    def resolve_all_wards(self, info, province_id=None):
        """Resolve tất cả wards, có thể filter theo province"""
        queryset = Ward.objects.select_related('province').order_by('province__name', 'name')
        if province_id:
            queryset = queryset.filter(province_id=province_id)
        return queryset
    
    def resolve_all_hamlets(self, info, ward_id=None):
        """Resolve tất cả hamlets, có thể filter theo ward"""
        queryset = Hamlet.objects.select_related('ward__province').order_by('ward__name', 'name')
        if ward_id:
            queryset = queryset.filter(ward_id=ward_id)
        return queryset
    
    # Resolvers cho custom queries
    def resolve_user_addresses(self, info, user_id):
        """Resolve addresses of a user sử dụng dataloader"""
        dataloaders = get_address_dataloaders(info)
        return dataloaders.addresses_by_user.load(int(user_id))
    
    def resolve_user_default_address(self, info, user_id):
        """Resolve default address of a user sử dụng dataloader"""
        dataloaders = get_address_dataloaders(info)
        return dataloaders.default_address_by_user.load(int(user_id))
    
    def resolve_wards_by_province(self, info, province_id):
        """Resolve wards in a province sử dụng dataloader"""
        dataloaders = get_address_dataloaders(info)
        return dataloaders.wards_by_province.load(int(province_id))
    
    def resolve_hamlets_by_ward(self, info, ward_id):
        """Resolve hamlets in a ward sử dụng dataloader"""
        dataloaders = get_address_dataloaders(info)
        return dataloaders.hamlets_by_ward.load(int(ward_id))
    
    def resolve_search_addresses(self, info, search_term, limit=20):
        """Tìm kiếm địa chỉ theo từ khóa"""
        return Address.objects.filter(
            Q(detail__icontains=search_term) |
            Q(hamlet__name__icontains=search_term) |
            Q(ward__name__icontains=search_term) |
            Q(province__name__icontains=search_term) |
            Q(user__username__icontains=search_term) |
            Q(user__first_name__icontains=search_term) |
            Q(user__last_name__icontains=search_term)
        ).select_related(
            'user', 'province', 'ward', 'hamlet', 'ward__province'
        ).order_by('-is_default', 'address_id')[:limit]


# Schema chính cho Address module
class AddressSchema(graphene.ObjectType):
    """Schema chính cho Address GraphQL API"""
    
    # Kế thừa queries và mutations
    class Query(AddressQuery):
        pass
    
    class Mutation(AddressMutation):
        pass


# Export schema để sử dụng trong main schema
address_schema = graphene.Schema(
    query=AddressSchema.Query,
    mutation=AddressSchema.Mutation
)