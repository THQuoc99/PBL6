from promise import Promise
from promise.dataloader import DataLoader
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Count, Prefetch
from collections import defaultdict

User = get_user_model()


class UserLoader(DataLoader):
    """DataLoader cho User"""
    
    def batch_load_fn(self, user_ids):
        """Load users theo batch"""
        users = User.objects.filter(id__in=user_ids).select_related()
        user_map = {user.id: user for user in users}
        return Promise.resolve([user_map.get(user_id) for user_id in user_ids])


class UserByUsernameLoader(DataLoader):
    """DataLoader cho User theo username"""
    
    def batch_load_fn(self, usernames):
        """Load users theo username batch"""
        users = User.objects.filter(username__in=usernames)
        user_map = {user.username: user for user in users}
        return Promise.resolve([user_map.get(username) for username in usernames])


class UserByEmailLoader(DataLoader):
    """DataLoader cho User theo email"""
    
    def batch_load_fn(self, emails):
        """Load users theo email batch"""
        users = User.objects.filter(email__in=emails)
        user_map = {user.email: user for user in users}
        return Promise.resolve([user_map.get(email) for email in emails])


class GroupLoader(DataLoader):
    """DataLoader cho Group"""
    
    def batch_load_fn(self, group_ids):
        """Load groups theo batch"""
        groups = Group.objects.filter(id__in=group_ids)
        group_map = {group.id: group for group in groups}
        return Promise.resolve([group_map.get(group_id) for group_id in group_ids])


class UserGroupsLoader(DataLoader):
    """DataLoader cho groups của user"""
    
    def batch_load_fn(self, user_ids):
        """Load groups cho nhiều users"""
        # Query tất cả relationships
        user_groups = User.objects.filter(
            id__in=user_ids
        ).prefetch_related('groups').values_list('id', 'groups__id', 'groups__name')
        
        # Tạo map từ user_id -> list groups
        groups_map = defaultdict(list)
        for user_id, group_id, group_name in user_groups:
            if group_id:  # Chỉ add nếu có group
                groups_map[user_id].append({
                    'id': group_id,
                    'name': group_name
                })
        
        # Return danh sách groups cho từng user_id theo đúng thứ tự
        return Promise.resolve([groups_map.get(user_id, []) for user_id in user_ids])


class GroupUsersLoader(DataLoader):
    """DataLoader cho users của group"""
    
    def batch_load_fn(self, group_ids):
        """Load users cho nhiều groups"""
        # Query tất cả relationships
        group_users = Group.objects.filter(
            id__in=group_ids
        ).prefetch_related('user_set').values_list(
            'id', 'user_set__id', 'user_set__username', 'user_set__email'
        )
        
        # Tạo map từ group_id -> list users
        users_map = defaultdict(list)
        for group_id, user_id, username, email in group_users:
            if user_id:  # Chỉ add nếu có user
                users_map[group_id].append({
                    'id': user_id,
                    'username': username,
                    'email': email
                })
        
        # Return danh sách users cho từng group_id theo đúng thứ tự
        return Promise.resolve([users_map.get(group_id, []) for group_id in group_ids])


class UserProductCountLoader(DataLoader):
    """DataLoader cho số lượng products của user"""
    
    def batch_load_fn(self, user_ids):
        """Load product count cho nhiều users"""
        # Import ở đây để tránh circular import
        from products.models import Product
        
        # Query count products cho từng user
        product_counts = Product.objects.filter(
            user_id__in=user_ids
        ).values('user_id').annotate(
            count=Count('id')
        ).values_list('user_id', 'count')
        
        # Tạo map từ user_id -> count
        count_map = dict(product_counts)
        
        # Return count cho từng user_id, default là 0
        return Promise.resolve([count_map.get(user_id, 0) for user_id in user_ids])


class UserPermissionsLoader(DataLoader):
    """DataLoader cho permissions của user"""
    
    def batch_load_fn(self, user_ids):
        """Load permissions cho nhiều users"""
        # Query permissions qua groups và user permissions
        from django.contrib.auth.models import Permission
        
        users_permissions = defaultdict(set)
        
        # Get permissions từ groups
        group_perms = User.objects.filter(
            id__in=user_ids
        ).prefetch_related(
            'groups__permissions'
        ).values_list('id', 'groups__permissions__codename')
        
        for user_id, perm_codename in group_perms:
            if perm_codename:
                users_permissions[user_id].add(perm_codename)
        
        # Get direct user permissions
        user_perms = User.objects.filter(
            id__in=user_ids
        ).prefetch_related(
            'user_permissions'
        ).values_list('id', 'user_permissions__codename')
        
        for user_id, perm_codename in user_perms:
            if perm_codename:
                users_permissions[user_id].add(perm_codename)
        
        # Convert sets to lists
        return Promise.resolve([
            list(users_permissions.get(user_id, set())) 
            for user_id in user_ids
        ])


class ActiveUserCountLoader(DataLoader):
    """DataLoader cho số lượng active users"""
    
    def batch_load_fn(self, keys):
        """Load active user count (keys có thể là bất kỳ, chỉ cần 1 key)"""
        count = User.objects.filter(is_active=True).count()
        return Promise.resolve([count] * len(keys))


class UserStatsLoader(DataLoader):
    """DataLoader cho thống kê user"""
    
    def batch_load_fn(self, user_ids):
        """Load stats cho nhiều users"""
        # Import ở đây để tránh circular import
        from products.models import Product
        from orders.models import Order
        
        stats_map = {}
        
        # Get product counts
        product_counts = Product.objects.filter(
            user_id__in=user_ids
        ).values('user_id').annotate(
            count=Count('id')
        ).values_list('user_id', 'count')
        
        product_count_map = dict(product_counts)
        
        # Get order counts (giả sử có field user trong Order)
        order_counts = Order.objects.filter(
            user_id__in=user_ids
        ).values('user_id').annotate(
            count=Count('id')
        ).values_list('user_id', 'count')
        
        order_count_map = dict(order_counts)
        
        # Combine stats
        for user_id in user_ids:
            stats_map[user_id] = {
                'product_count': product_count_map.get(user_id, 0),
                'order_count': order_count_map.get(user_id, 0),
            }
        
        return Promise.resolve([stats_map.get(user_id, {
            'product_count': 0,
            'order_count': 0,
        }) for user_id in user_ids])


# Factory function để tạo loaders
def create_user_loaders():
    """Tạo tất cả user loaders"""
    return {
        'user_loader': UserLoader(),
        'user_by_username_loader': UserByUsernameLoader(),
        'user_by_email_loader': UserByEmailLoader(),
        'group_loader': GroupLoader(),
        'user_groups_loader': UserGroupsLoader(),
        'group_users_loader': GroupUsersLoader(),
        'user_product_count_loader': UserProductCountLoader(),
        'user_permissions_loader': UserPermissionsLoader(),
        'active_user_count_loader': ActiveUserCountLoader(),
        'user_stats_loader': UserStatsLoader(),
    }


# Helper functions để get loaders từ context
def get_user_loader(info):
    """Get user loader từ GraphQL context"""
    context = info.context
    if not hasattr(context, 'user_loaders'):
        context.user_loaders = create_user_loaders()
    return context.user_loaders['user_loader']


def get_user_by_username_loader(info):
    """Get user by username loader từ GraphQL context"""
    context = info.context
    if not hasattr(context, 'user_loaders'):
        context.user_loaders = create_user_loaders()
    return context.user_loaders['user_by_username_loader']


def get_user_by_email_loader(info):
    """Get user by email loader từ GraphQL context"""
    context = info.context
    if not hasattr(context, 'user_loaders'):
        context.user_loaders = create_user_loaders()
    return context.user_loaders['user_by_email_loader']


def get_group_loader(info):
    """Get group loader từ GraphQL context"""
    context = info.context
    if not hasattr(context, 'user_loaders'):
        context.user_loaders = create_user_loaders()
    return context.user_loaders['group_loader']


def get_user_groups_loader(info):
    """Get user groups loader từ GraphQL context"""
    context = info.context
    if not hasattr(context, 'user_loaders'):
        context.user_loaders = create_user_loaders()
    return context.user_loaders['user_groups_loader']


def get_group_users_loader(info):
    """Get group users loader từ GraphQL context"""
    context = info.context
    if not hasattr(context, 'user_loaders'):
        context.user_loaders = create_user_loaders()
    return context.user_loaders['group_users_loader']


def get_user_product_count_loader(info):
    """Get user product count loader từ GraphQL context"""
    context = info.context
    if not hasattr(context, 'user_loaders'):
        context.user_loaders = create_user_loaders()
    return context.user_loaders['user_product_count_loader']


def get_user_permissions_loader(info):
    """Get user permissions loader từ GraphQL context"""
    context = info.context
    if not hasattr(context, 'user_loaders'):
        context.user_loaders = create_user_loaders()
    return context.user_loaders['user_permissions_loader']


def get_user_stats_loader(info):
    """Get user stats loader từ GraphQL context"""
    context = info.context
    if not hasattr(context, 'user_loaders'):
        context.user_loaders = create_user_loaders()
    return context.user_loaders['user_stats_loader']


# Export all
__all__ = [
    'UserLoader',
    'UserByUsernameLoader', 
    'UserByEmailLoader',
    'GroupLoader',
    'UserGroupsLoader',
    'GroupUsersLoader',
    'UserProductCountLoader',
    'UserPermissionsLoader',
    'ActiveUserCountLoader',
    'UserStatsLoader',
    'create_user_loaders',
    'get_user_loader',
    'get_user_by_username_loader',
    'get_user_by_email_loader',
    'get_group_loader',
    'get_user_groups_loader',
    'get_group_users_loader',
    'get_user_product_count_loader',
    'get_user_permissions_loader',
    'get_user_stats_loader',
]