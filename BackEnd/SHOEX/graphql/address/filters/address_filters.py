import django_filters
from django.db.models import Q, Count
from django.db import models
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from address.models import Province, Ward, Hamlet, Address


class ProvinceFilter(django_filters.FilterSet):
    """Filter cho Province"""
    
    # Tìm kiếm theo tên
    name_contains = django_filters.CharFilter(
        field_name='name', 
        lookup_expr='icontains',
        help_text="Tìm tỉnh/thành có chứa từ khóa trong tên"
    )
    
    name_exact = django_filters.CharFilter(
        field_name='name',
        lookup_expr='exact',
        help_text="Tìm tỉnh/thành có tên chính xác"
    )
    
    # Filter theo số lượng wards
    min_wards = django_filters.NumberFilter(
        method='filter_min_wards',
        help_text="Tỉnh/thành có ít nhất n phường/xã"
    )
    
    max_wards = django_filters.NumberFilter(
        method='filter_max_wards',
        help_text="Tỉnh/thành có nhiều nhất n phường/xã"
    )
    
    class Meta:
        model = Province
        fields = {
            'province_id': ['exact'],
            'name': ['exact', 'icontains', 'istartswith'],
        }
    
    def filter_min_wards(self, queryset, name, value):
        """Filter tỉnh có ít nhất n wards"""
        if value is not None:
            return queryset.annotate(
                ward_count=Count('wards')
            ).filter(ward_count__gte=value)
        return queryset
    
    def filter_max_wards(self, queryset, name, value):
        """Filter tỉnh có nhiều nhất n wards"""
        if value is not None:
            return queryset.annotate(
                ward_count=Count('wards')
            ).filter(ward_count__lte=value)
        return queryset


class WardFilter(django_filters.FilterSet):
    """Filter cho Ward"""
    
    # Tìm kiếm theo tên
    name_contains = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text="Tìm phường/xã có chứa từ khóa trong tên"
    )
    
    # Filter theo province
    province_name = django_filters.CharFilter(
        field_name='province__name',
        lookup_expr='icontains',
        help_text="Tìm theo tên tỉnh/thành"
    )
    
    province_id = django_filters.NumberFilter(
        field_name='province__province_id',
        help_text="Filter theo ID tỉnh/thành"
    )
    
    # Filter theo số lượng hamlets
    min_hamlets = django_filters.NumberFilter(
        method='filter_min_hamlets',
        help_text="Phường/xã có ít nhất n thôn/xóm"
    )
    
    max_hamlets = django_filters.NumberFilter(
        method='filter_max_hamlets',
        help_text="Phường/xã có nhiều nhất n thôn/xóm"
    )
    
    class Meta:
        model = Ward
        fields = {
            'ward_id': ['exact'],
            'name': ['exact', 'icontains', 'istartswith'],
            'province': ['exact'],
        }
    
    def filter_min_hamlets(self, queryset, name, value):
        """Filter ward có ít nhất n hamlets"""
        if value is not None:
            return queryset.annotate(
                hamlet_count=Count('hamlets')
            ).filter(hamlet_count__gte=value)
        return queryset
    
    def filter_max_hamlets(self, queryset, name, value):
        """Filter ward có nhiều nhất n hamlets"""
        if value is not None:
            return queryset.annotate(
                hamlet_count=Count('hamlets')
            ).filter(hamlet_count__lte=value)
        return queryset


class HamletFilter(django_filters.FilterSet):
    """Filter cho Hamlet"""
    
    # Tìm kiếm theo tên
    name_contains = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text="Tìm thôn/xóm có chứa từ khóa trong tên"
    )
    
    # Filter theo ward
    ward_name = django_filters.CharFilter(
        field_name='ward__name',
        lookup_expr='icontains',
        help_text="Tìm theo tên phường/xã"
    )
    
    ward_id = django_filters.NumberFilter(
        field_name='ward__ward_id',
        help_text="Filter theo ID phường/xã"
    )
    
    # Filter theo province
    province_name = django_filters.CharFilter(
        field_name='ward__province__name',
        lookup_expr='icontains',
        help_text="Tìm theo tên tỉnh/thành"
    )
    
    province_id = django_filters.NumberFilter(
        field_name='ward__province__province_id',
        help_text="Filter theo ID tỉnh/thành"
    )
    
    class Meta:
        model = Hamlet
        fields = {
            'hamlet_id': ['exact'],
            'name': ['exact', 'icontains', 'istartswith'],
            'ward': ['exact'],
        }


class AddressFilter(django_filters.FilterSet):
    """Filter cho Address"""
    
    # Filter theo user
    user_id = django_filters.NumberFilter(
        field_name='user__id',
        help_text="Filter theo ID người dùng"
    )
    
    user_username = django_filters.CharFilter(
        field_name='user__username',
        lookup_expr='icontains',
        help_text="Tìm theo username"
    )
    
    # Filter theo địa chỉ chi tiết
    detail_contains = django_filters.CharFilter(
        field_name='detail',
        lookup_expr='icontains',
        help_text="Tìm trong địa chỉ chi tiết"
    )
    
    # Filter theo province
    province_name = django_filters.CharFilter(
        field_name='province__name',
        lookup_expr='icontains',
        help_text="Tìm theo tên tỉnh/thành"
    )
    
    province_id = django_filters.NumberFilter(
        field_name='province__province_id',
        help_text="Filter theo ID tỉnh/thành"
    )
    
    # Filter theo ward
    ward_name = django_filters.CharFilter(
        field_name='ward__name',
        lookup_expr='icontains',
        help_text="Tìm theo tên phường/xã"
    )
    
    ward_id = django_filters.NumberFilter(
        field_name='ward__ward_id',
        help_text="Filter theo ID phường/xã"
    )
    
    # Filter theo hamlet
    hamlet_name = django_filters.CharFilter(
        field_name='hamlet__name',
        lookup_expr='icontains',
        help_text="Tìm theo tên thôn/xóm"
    )
    
    hamlet_id = django_filters.NumberFilter(
        field_name='hamlet__hamlet_id',
        help_text="Filter theo ID thôn/xóm"
    )
    
    # Filter theo is_default
    is_default = django_filters.BooleanFilter(
        field_name='is_default',
        help_text="Filter địa chỉ mặc định"
    )
    
    # Filter full-text search
    search = django_filters.CharFilter(
        method='filter_search',
        help_text="Tìm kiếm toàn văn trong địa chỉ"
    )
    
    class Meta:
        model = Address
        fields = {
            'address_id': ['exact'],
            'is_default': ['exact'],
            'user': ['exact'],
            'province': ['exact'],
            'ward': ['exact'],
            'hamlet': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        """Full-text search trong địa chỉ"""
        if value:
            return queryset.filter(
                Q(detail__icontains=value) |
                Q(hamlet__name__icontains=value) |
                Q(ward__name__icontains=value) |
                Q(province__name__icontains=value) |
                Q(user__username__icontains=value) |
                Q(user__first_name__icontains=value) |
                Q(user__last_name__icontains=value)
            )
        return queryset


# Input types cho GraphQL filters
class ProvinceFilterInput(graphene.InputObjectType):
    """Input cho Province filter"""
    name_contains = graphene.String()
    name_exact = graphene.String()
    min_wards = graphene.Int()
    max_wards = graphene.Int()


class WardFilterInput(graphene.InputObjectType):
    """Input cho Ward filter"""
    name_contains = graphene.String()
    province_name = graphene.String()
    province_id = graphene.ID()
    min_hamlets = graphene.Int()
    max_hamlets = graphene.Int()


class HamletFilterInput(graphene.InputObjectType):
    """Input cho Hamlet filter"""
    name_contains = graphene.String()
    ward_name = graphene.String()
    ward_id = graphene.ID()
    province_name = graphene.String()
    province_id = graphene.ID()


class AddressFilterInput(graphene.InputObjectType):
    """Input cho Address filter"""
    user_id = graphene.ID()
    user_username = graphene.String()
    detail_contains = graphene.String()
    province_name = graphene.String()
    province_id = graphene.ID()
    ward_name = graphene.String()
    ward_id = graphene.ID()
    hamlet_name = graphene.String()
    hamlet_id = graphene.ID()
    is_default = graphene.Boolean()
    search = graphene.String()