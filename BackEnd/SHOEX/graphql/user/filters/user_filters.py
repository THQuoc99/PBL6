import graphene
from graphene import InputObjectType
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class UserFilterInput(InputObjectType):
    """Bộ lọc cho User"""
    
    # Text filters
    username = graphene.String(description="Lọc theo username (chính xác)")
    username_icontains = graphene.String(description="Lọc theo username (chứa)")
    email = graphene.String(description="Lọc theo email (chính xác)")
    email_icontains = graphene.String(description="Lọc theo email (chứa)")
    first_name_icontains = graphene.String(description="Lọc theo họ (chứa)")
    last_name_icontains = graphene.String(description="Lọc theo tên (chứa)")
    full_name_icontains = graphene.String(description="Lọc theo tên đầy đủ (chứa)")
    phone_icontains = graphene.String(description="Lọc theo số điện thoại (chứa)")
    role = graphene.String(description="Lọc theo vai trò (buyer, seller, admin)")
    
    # Boolean filters
    is_active = graphene.Boolean(description="Lọc theo trạng thái hoạt động")
    is_staff = graphene.Boolean(description="Lọc theo quyền staff")
    is_superuser = graphene.Boolean(description="Lọc theo quyền superuser")
    
    # Date filters
    date_joined_gte = graphene.DateTime(description="Ngày tham gia từ")
    date_joined_lte = graphene.DateTime(description="Ngày tham gia đến")
    last_login_gte = graphene.DateTime(description="Đăng nhập cuối từ")
    last_login_lte = graphene.DateTime(description="Đăng nhập cuối đến")
    
    # Relationship filters
    groups = graphene.List(graphene.ID, description="Lọc theo nhóm")
    has_products = graphene.Boolean(description="Có sản phẩm hay không")
    
    # Search
    search = graphene.String(description="Tìm kiếm trong username, email, tên")

    @staticmethod
    def filter_queryset(queryset, filter_input):
        """Áp dụng filter vào queryset"""
        if not filter_input:
            return queryset
        
        # Text filters
        if filter_input.get('username'):
            queryset = queryset.filter(username=filter_input.username)
        
        if filter_input.get('username_icontains'):
            queryset = queryset.filter(username__icontains=filter_input.username_icontains)
        
        if filter_input.get('email'):
            queryset = queryset.filter(email=filter_input.email)
        
        if filter_input.get('email_icontains'):
            queryset = queryset.filter(email__icontains=filter_input.email_icontains)
        
        if filter_input.get('first_name_icontains'):
            queryset = queryset.filter(first_name__icontains=filter_input.first_name_icontains)
        
        if filter_input.get('last_name_icontains'):
            queryset = queryset.filter(last_name__icontains=filter_input.last_name_icontains)
        
        # Custom fields filters
        if filter_input.get('full_name_icontains'):
            queryset = queryset.filter(full_name__icontains=filter_input.full_name_icontains)
        
        if filter_input.get('phone_icontains'):
            queryset = queryset.filter(phone__icontains=filter_input.phone_icontains)
        
        if filter_input.get('role'):
            queryset = queryset.filter(role=filter_input.role)
        
        # Boolean filters
        if filter_input.get('is_active') is not None:
            queryset = queryset.filter(is_active=filter_input.is_active)
        
        if filter_input.get('is_staff') is not None:
            queryset = queryset.filter(is_staff=filter_input.is_staff)
        
        if filter_input.get('is_superuser') is not None:
            queryset = queryset.filter(is_superuser=filter_input.is_superuser)
        
        # Date filters
        if filter_input.get('date_joined_gte'):
            queryset = queryset.filter(date_joined__gte=filter_input.date_joined_gte)
        
        if filter_input.get('date_joined_lte'):
            queryset = queryset.filter(date_joined__lte=filter_input.date_joined_lte)
        
        if filter_input.get('last_login_gte'):
            queryset = queryset.filter(last_login__gte=filter_input.last_login_gte)
        
        if filter_input.get('last_login_lte'):
            queryset = queryset.filter(last_login__lte=filter_input.last_login_lte)
        
        # Relationship filters
        if filter_input.get('groups'):
            queryset = queryset.filter(groups__id__in=filter_input.groups).distinct()
        
        if filter_input.get('has_products') is not None:
            if filter_input.has_products:
                queryset = queryset.filter(products__isnull=False).distinct()
            else:
                queryset = queryset.filter(products__isnull=True)
        
        # Search
        if filter_input.get('search'):
            search_term = filter_input.search
            queryset = queryset.filter(
                Q(username__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(full_name__icontains=search_term) |
                Q(phone__icontains=search_term)
            )
        
        return queryset


class GroupFilterInput(InputObjectType):
    """Bộ lọc cho Group"""
    
    # Text filters
    name = graphene.String(description="Lọc theo tên nhóm (chính xác)")
    name_icontains = graphene.String(description="Lọc theo tên nhóm (chứa)")
    
    # Relationship filters
    has_users = graphene.Boolean(description="Có user hay không")
    
    # Search
    search = graphene.String(description="Tìm kiếm trong tên nhóm")

    @staticmethod
    def filter_queryset(queryset, filter_input):
        """Áp dụng filter vào queryset"""
        if not filter_input:
            return queryset
        
        # Text filters
        if filter_input.get('name'):
            queryset = queryset.filter(name=filter_input.name)
        
        if filter_input.get('name_icontains'):
            queryset = queryset.filter(name__icontains=filter_input.name_icontains)
        
        # Relationship filters
        if filter_input.get('has_users') is not None:
            if filter_input.has_users:
                queryset = queryset.filter(user__isnull=False).distinct()
            else:
                queryset = queryset.filter(user__isnull=True)
        
        # Search
        if filter_input.get('search'):
            search_term = filter_input.search
            queryset = queryset.filter(name__icontains=search_term)
        
        return queryset


# Sort options
USER_SORT_CHOICES = [
    ('USERNAME_ASC', 'Username A-Z'),
    ('USERNAME_DESC', 'Username Z-A'),
    ('EMAIL_ASC', 'Email A-Z'),
    ('EMAIL_DESC', 'Email Z-A'),
    ('FIRST_NAME_ASC', 'Họ A-Z'),
    ('FIRST_NAME_DESC', 'Họ Z-A'),
    ('LAST_NAME_ASC', 'Tên A-Z'),
    ('LAST_NAME_DESC', 'Tên Z-A'),
    ('DATE_JOINED_ASC', 'Tham gia cũ nhất'),
    ('DATE_JOINED_DESC', 'Tham gia mới nhất'),
    ('LAST_LOGIN_ASC', 'Đăng nhập cũ nhất'),
    ('LAST_LOGIN_DESC', 'Đăng nhập mới nhất'),
]

GROUP_SORT_CHOICES = [
    ('NAME_ASC', 'Tên A-Z'),
    ('NAME_DESC', 'Tên Z-A'),
    ('USER_COUNT_ASC', 'Ít user nhất'),
    ('USER_COUNT_DESC', 'Nhiều user nhất'),
]


def apply_user_sort(queryset, sort_by):
    """Áp dụng sort cho User queryset"""
    sort_mapping = {
        'USERNAME_ASC': 'username',
        'USERNAME_DESC': '-username',
        'EMAIL_ASC': 'email',
        'EMAIL_DESC': '-email',
        'FIRST_NAME_ASC': 'first_name',
        'FIRST_NAME_DESC': '-first_name',
        'LAST_NAME_ASC': 'last_name',
        'LAST_NAME_DESC': '-last_name',
        'DATE_JOINED_ASC': 'date_joined',
        'DATE_JOINED_DESC': '-date_joined',
        'LAST_LOGIN_ASC': 'last_login',
        'LAST_LOGIN_DESC': '-last_login',
    }
    
    if sort_by and sort_by in sort_mapping:
        return queryset.order_by(sort_mapping[sort_by])
    
    # Default sort
    return queryset.order_by('-date_joined')


def apply_group_sort(queryset, sort_by):
    """Áp dụng sort cho Group queryset"""
    sort_mapping = {
        'NAME_ASC': 'name',
        'NAME_DESC': '-name',
    }
    
    if sort_by and sort_by in sort_mapping:
        return queryset.order_by(sort_mapping[sort_by])
    elif sort_by == 'USER_COUNT_ASC':
        return queryset.annotate(
            user_count=Count('user')
        ).order_by('user_count')
    elif sort_by == 'USER_COUNT_DESC':
        return queryset.annotate(
            user_count=Count('user')
        ).order_by('-user_count')
    
    # Default sort
    return queryset.order_by('name')


# Export all
__all__ = [
    'UserFilterInput',
    'GroupFilterInput',
    'USER_SORT_CHOICES',
    'GROUP_SORT_CHOICES',
    'apply_user_sort',
    'apply_group_sort'
]