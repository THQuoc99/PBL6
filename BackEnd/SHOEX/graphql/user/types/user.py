import graphene
# from graphene import relay  # ← Không cần nữa
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class GroupType(DjangoObjectType):
    """Nhóm người dùng"""
    class Meta:
        model = Group
        fields = '__all__'
        # interfaces = (relay.Node,)  # ← Đã loại bỏ

    user_count = graphene.Int(description="Số lượng người dùng trong nhóm")
    
    def resolve_user_count(self, info):
        """Đếm số lượng user trong group"""
        return self.user_set.count()


class UserType(DjangoObjectType):
    """Người dùng hệ thống"""
    is_authenticated = graphene.Boolean(description="User này có đang đăng nhập không")
    class Meta:
        model = User
        fields = "__all__"
        # interfaces = (relay.Node,)  # ← Đã loại bỏ

    # Thêm các trường tùy chỉnh
    role_display = graphene.String(description="Hiển thị vai trò")
    display_name = graphene.String(description="Tên hiển thị")
    initials = graphene.String(description="Chữ cái đầu tên")
    product_count = graphene.Int(description="Số lượng sản phẩm đã tạo")
    order_count = graphene.Int(description="Số lượng đơn hàng")
    is_seller = graphene.Boolean(description="Có phải người bán không")
    is_customer = graphene.Boolean(description="Có phải khách hàng không")
    avatar_url = graphene.String(description="URL avatar")
    
    # Relationship fields
    user_groups = graphene.List(GroupType, description="Danh sách nhóm của user")
    def resolve_is_authenticated(self, info):
        # CHỈ khi query "me" thì mới đúng nghĩa
        return self.is_authenticated  
    def resolve_role_display(self, info):
        """Hiển thị role dễ đọc"""
        return self.get_role_display() if hasattr(self, 'get_role_display') else self.role
    
    def resolve_display_name(self, info):
        """Tên hiển thị ưu tiên"""
        if hasattr(self, 'full_name') and self.full_name:
            return self.full_name
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def resolve_initials(self, info):
        """Lấy chữ cái đầu của tên"""
        if hasattr(self, 'full_name') and self.full_name:
            words = self.full_name.split()
            if len(words) >= 2:
                return f"{words[0][0]}{words[-1][0]}".upper()
            elif len(words) == 1:
                return words[0][0].upper()
        elif self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[0].upper()
        elif self.last_name:
            return self.last_name[0].upper()
        return self.username[0].upper() if self.username else "U"
    
    def resolve_product_count(self, info):
        """Đếm số sản phẩm user đã tạo"""
        return self.products.filter(is_active=True).count()
    
    def resolve_order_count(self, info):
        """Đếm số đơn hàng của user"""
        # TODO: Implement when orders app is ready
        return 0
    
    def resolve_is_seller(self, info):
        """Kiểm tra user có phải seller không"""
        if hasattr(self, 'role'):
            return self.role == 'seller'
        return self.products.exists() if hasattr(self, 'products') else False
    
    def resolve_is_customer(self, info):
        """Kiểm tra user có phải customer không"""
        if hasattr(self, 'role'):
            return self.role == 'buyer'
        return True
    
    def resolve_avatar_url(self, info):
        """URL avatar (placeholder)"""
        # TODO: Implement avatar logic
        # Duplicate logic từ resolve_display_name vì không thể gọi resolver khác
        if hasattr(self, 'full_name') and self.full_name:
            display_name = self.full_name
        elif self.first_name and self.last_name:
            display_name = f"{self.first_name} {self.last_name}"
        else:
            display_name = self.username
            
        return f"https://ui-avatars.com/api/?name={display_name}&background=random"
    
    def resolve_user_groups(self, info):
        """Lấy danh sách groups của user"""
        return self.groups.all()


class UserProfileType(graphene.ObjectType):
    """Profile thống kê của user"""
    user = graphene.Field(UserType, description="Thông tin user")
    total_products = graphene.Int(description="Tổng số sản phẩm")
    total_variants = graphene.Int(description="Tổng số biến thể")
    total_orders = graphene.Int(description="Tổng số đơn hàng")
    total_revenue = graphene.Decimal(description="Tổng doanh thu")
    join_date = graphene.DateTime(description="Ngày tham gia")
    last_activity = graphene.DateTime(description="Hoạt động cuối")
    
    @staticmethod
    def resolve_total_products(root, info):
        """Tổng số sản phẩm"""
        return root.products.filter(is_active=True).count()
    
    @staticmethod
    def resolve_total_variants(root, info):
        """Tổng số biến thể"""
        from products.models import ProductVariant
        return ProductVariant.objects.filter(
            product__seller=root,
            is_active=True
        ).count()
    
    @staticmethod
    def resolve_total_orders(root, info):
        """Tổng số đơn hàng"""
        # TODO: Implement when orders app is ready
        return 0
    
    @staticmethod
    def resolve_total_revenue(root, info):
        """Tổng doanh thu"""
        # TODO: Implement when orders app is ready
        return 0
    
    @staticmethod
    def resolve_join_date(root, info):
        """Ngày tham gia"""
        return root.date_joined
    
    @staticmethod
    def resolve_last_activity(root, info):
        """Hoạt động cuối cùng"""
        return root.last_login


# Connection types for pagination (simplified without Relay)
# Note: Nếu không dùng Relay, có thể không cần Connection types
# hoặc tự định nghĩa pagination response types đơn giản hơn

class UserListType(graphene.ObjectType):
    """Simple pagination for users without Relay"""
    users = graphene.List(UserType)
    total_count = graphene.Int()
    has_next_page = graphene.Boolean()
    has_previous_page = graphene.Boolean()


class GroupListType(graphene.ObjectType):
    """Simple pagination for groups without Relay"""
    groups = graphene.List(GroupType)  
    total_count = graphene.Int()
    has_next_page = graphene.Boolean()
    has_previous_page = graphene.Boolean()


# Aliases for compatibility (updated for non-Relay)
UserCountableConnection = UserListType
GroupCountableConnection = GroupListType


# Export all types
__all__ = [
    'UserType',
    'GroupType', 
    'UserProfileType',
    'UserListType',
    'GroupListType', 
    'UserCountableConnection',
    'GroupCountableConnection'
]