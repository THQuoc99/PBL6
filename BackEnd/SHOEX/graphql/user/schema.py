import graphene
from graphene import ObjectType, Field, List, String, Int, Boolean, ID
from graphene_django import DjangoConnectionField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q

# Import types
from .types.user import (
    UserType, 
    GroupType, 
    UserListType,
    GroupListType,
    UserProfileType
)

# Import mutations
from .mutations.user_mutations import (
    UserCreate,
    UserUpdate,
    UserDelete,
    PasswordChange,
    GroupCreate,
    GroupUpdate,
    GroupDelete,
    UserGroupAdd,
    UserGroupRemove,
    LoginMutation,
    LogoutMutation
)

# Import bulk mutations
from .bulk_mutations.user_bulk_mutations import (
    BulkUserCreate,
    BulkUserUpdate,
    BulkUserDelete,
    BulkUserActivate
)

# Import filters
from .filters.user_filters import (
    UserFilterInput,
    GroupFilterInput,
    apply_user_sort,
    apply_group_sort
)

# Import loaders
from .dataloaders.user_loaders import (
    get_user_loader,
    get_group_loader,
    get_user_groups_loader,
    get_user_product_count_loader
)

User = get_user_model()


class UserQuery(ObjectType):
    """GraphQL queries cho User module"""
    
    # Single object queries
    user = Field(UserType, id=ID(required=True))
    user_by_pk = Field(UserType, pk=Int(required=True), description="Get user by database ID")
    group = Field(GroupType, id=ID(required=True))
    me = Field(UserType)
    
    # List queries with filtering  
    users = List(
        UserType,
        filter_input=UserFilterInput(),
        sort_by=String(),
        search=String()
    )
    
    groups = List(
        GroupType,
        filter_input=GroupFilterInput(),
        sort_by=String(),
        search=String()
    )
    
    # Specific queries
    active_users = List(UserType)
    staff_users = List(UserType)
    users_by_group = List(
        UserType,
        group_id=ID(required=True)
    )
    
    # Statistics
    user_count = Int()
    active_user_count = Int()
    staff_user_count = Int()
    group_count = Int()
    
    # User profile
    user_profile = Field(UserProfileType, user_id=ID())

    # def resolve_user(self, info, id):
    #     """Lấy user theo ID"""
    #     try:
    #         return get_user_loader(info).load(id)
    #     except:
    #         return None
    def resolve_user(self, info, id):
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None
    
    def resolve_user_by_pk(self, info, pk):
        """Lấy user theo database ID"""
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None


    def resolve_group(self, info, id):
        """Lấy group theo ID"""
        try:
            return Group.objects.get(pk=id)
        except Group.DoesNotExist:
            return None

    def resolve_me(self, info):
        """Lấy thông tin user hiện tại"""
        user = info.context.user
        if user.is_authenticated:
            return user
        return None

    def resolve_users(self, info, filter=None, sort_by=None, search=None, **kwargs):
        """Lấy danh sách users với filter và sort"""
        queryset = User.objects.all()
        
        # Apply search
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Apply filters
        if filter:
            from .filters.user_filters import UserFilterInput
            queryset = UserFilterInput.filter_queryset(queryset, filter)
        
        # Apply sorting
        queryset = apply_user_sort(queryset, sort_by)
        
        return queryset

    def resolve_groups(self, info, filter=None, sort_by=None, search=None, **kwargs):
        """Lấy danh sách groups với filter và sort"""
        queryset = Group.objects.all()
        
        # Apply search
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Apply filters
        if filter:
            from .filters.user_filters import GroupFilterInput
            queryset = GroupFilterInput.filter_queryset(queryset, filter)
            
        # Apply sorting
        queryset = apply_group_sort(queryset, sort_by)
        
        return queryset

    def resolve_active_users(self, info, **kwargs):
        """Lấy danh sách users đang hoạt động"""
        return User.objects.filter(is_active=True).order_by('-date_joined')

    def resolve_staff_users(self, info, **kwargs):
        """Lấy danh sách staff users"""
        return User.objects.filter(is_staff=True).order_by('-date_joined')

    def resolve_users_by_group(self, info, group_id, **kwargs):
        """Lấy users trong group"""
        try:
            group = Group.objects.get(id=group_id)
            return group.user_set.all().order_by('username')
        except Group.DoesNotExist:
            return User.objects.none()

    def resolve_user_count(self, info):
        """Tổng số users"""
        return User.objects.count()

    def resolve_active_user_count(self, info):
        """Số users đang hoạt động"""
        return User.objects.filter(is_active=True).count()

    def resolve_staff_user_count(self, info):
        """Số staff users"""
        return User.objects.filter(is_staff=True).count()

    def resolve_group_count(self, info):
        """Tổng số groups"""
        return Group.objects.count()

    def resolve_user_profile(self, info, user_id=None):
        """Lấy user profile"""
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                return UserProfileType(user=user)
            except User.DoesNotExist:
                return None
        else:
            # Return current user profile
            user = info.context.user
            if user.is_authenticated:
                return UserProfileType(user=user)
        return None


class UserMutation(ObjectType):
    """GraphQL mutations cho User module"""
    
    # Single user mutations
    user_create = UserCreate.Field()
    user_update = UserUpdate.Field()
    user_delete = UserDelete.Field()
    password_change = PasswordChange.Field()
    
    # Group mutations
    group_create = GroupCreate.Field()
    group_update = GroupUpdate.Field() 
    group_delete = GroupDelete.Field()
    
    # User-Group relationship mutations
    user_group_add = UserGroupAdd.Field()
    user_group_remove = UserGroupRemove.Field()
    
    # Authentication mutations
    login = LoginMutation.Field()
    logout = LogoutMutation.Field()
    
    # Bulk mutations
    bulk_user_create = BulkUserCreate.Field()
    bulk_user_update = BulkUserUpdate.Field()
    bulk_user_delete = BulkUserDelete.Field()
    bulk_user_activate = BulkUserActivate.Field()


# Main schema for user module
user_schema = graphene.Schema(
    query=UserQuery,
    mutation=UserMutation
)


# Export all
__all__ = [
    'UserQuery',
    'UserMutation', 
    'user_schema'
]