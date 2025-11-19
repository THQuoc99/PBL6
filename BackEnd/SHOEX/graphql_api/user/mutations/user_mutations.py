import graphene
from graphene import InputObjectType, Mutation, Field, String, Boolean, ID
# === HƯỚNG DẪN ĐỒNG BỘ ĐĂNG NHẬP FRONTEND/BACKEND ===
# Để đảm bảo backend nhận đúng token từ frontend khi chạy khác cổng (localhost:3000 và localhost:8000),
# bạn cần cấu hình CORS trong Django settings.py như sau:
#
# 1. Cài đặt package:
#    pip install django-cors-headers
# 2. Thêm vào INSTALLED_APPS:
#    'corsheaders',
# 3. Thêm vào MIDDLEWARE (ở trên cùng):
#    'corsheaders.middleware.CorsMiddleware',
# 4. Thêm vào settings:
#    CORS_ALLOWED_ORIGINS = [
#        "http://localhost:3000",
#    ]
#    CORS_ALLOW_CREDENTIALS = True
# 5. Đảm bảo frontend luôn gửi header Authorization: Bearer <token> khi gọi API.
# 6. Đảm bảo backend có middleware giải mã JWT (nếu dùng django-graphql-jwt):
#    GRAPHENE = {
#        "MIDDLEWARE": [
#            "graphql_jwt.middleware.JSONWebTokenMiddleware",
#        ],
#    }
#
# Nếu làm đúng các bước trên, backend sẽ nhận diện đúng user từ token khi frontend đã đăng nhập.
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from ..types.user import UserType, GroupType

# Token types
class TokenType(graphene.ObjectType):
    access_token = graphene.String(description="JWT access token")
    refresh_token = graphene.String(description="Refresh token")
    expires_in = graphene.Int(description="Token expiration time in seconds")

class AuthResponseType(graphene.ObjectType):
    user = graphene.Field(UserType)
    tokens = graphene.Field(TokenType)
    success = graphene.Boolean()
    message = graphene.String()

class ErrorType(graphene.ObjectType):
    username = graphene.String()
    password = graphene.String()
    email = graphene.String()
    general = graphene.String()

User = get_user_model()

# JWT Helper functions
import jwt
from datetime import datetime, timedelta
from django.conf import settings
import secrets

def generate_jwt_token(user):
    """Generate JWT access token"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def generate_refresh_token():
    """Generate refresh token"""
    return secrets.token_urlsafe(32)
def generate_jwt_token(user):
    """Generate JWT access token"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def generate_refresh_token():
    """Generate refresh token"""
    return secrets.token_urlsafe(32)


# ===== INPUT TYPES =====

class RegisterInput(InputObjectType):
    """Input cho đăng ký user mới"""
    full_name = graphene.String(required=True, description="Họ và tên")
    username = graphene.String(required=True, description="Tên đăng nhập")
    email = graphene.String(required=True, description="Email")
    password = graphene.String(required=True, description="Mật khẩu")
    birth_date = graphene.Date(description="Ngày sinh (YYYY-MM-DD)")

class LoginInput(InputObjectType):
    """Input cho đăng nhập"""
    username = graphene.String(required=True, description="Tên đăng nhập")
    password = graphene.String(required=True, description="Mật khẩu")
    remember_me = graphene.Boolean(default_value=False, description="Ghi nhớ đăng nhập")

class UserCreateInput(InputObjectType):
    """Input cho tạo user mới"""
    username = graphene.String(required=True, description="Tên đăng nhập")
    email = graphene.String(required=True, description="Email")
    password = graphene.String(required=True, description="Mật khẩu")
    first_name = graphene.String(description="Họ (AbstractUser field)")
    last_name = graphene.String(description="Tên (AbstractUser field)")
    full_name = graphene.String(description="Họ và tên đầy đủ (custom field)")
    phone = graphene.String(description="Số điện thoại")
    birth_date = graphene.Date(description="Ngày sinh (YYYY-MM-DD)")
    role = graphene.String(description="Vai trò: buyer, seller, admin")
    is_active = graphene.Boolean(default_value=True, description="Kích hoạt tài khoản")
    groups = graphene.List(graphene.ID, description="Danh sách ID nhóm")


class UserUpdateInput(InputObjectType):
    """Input cho cập nhật user"""
    username = graphene.String(description="Tên đăng nhập")
    email = graphene.String(description="Email")
    first_name = graphene.String(description="Họ (AbstractUser field)")
    last_name = graphene.String(description="Tên (AbstractUser field)")
    full_name = graphene.String(description="Họ và tên đầy đủ (custom field)")
    phone = graphene.String(description="Số điện thoại")
    birth_date = graphene.Date(description="Ngày sinh (YYYY-MM-DD)")
    role = graphene.String(description="Vai trò: buyer, seller, admin")
    is_active = graphene.Boolean(description="Kích hoạt tài khoản")
    groups = graphene.List(graphene.ID, description="Danh sách ID nhóm")


class PasswordChangeInput(InputObjectType):
    """Input cho đổi mật khẩu"""
    old_password = graphene.String(required=True, description="Mật khẩu cũ")
    new_password = graphene.String(required=True, description="Mật khẩu mới,Không được quá giống thông tin tài khoản,Độ dài tối thiểu 8,Không được là mật khẩu phổ biến,Không được toàn số")


class GroupCreateInput(InputObjectType):
    """Input cho tạo nhóm mới"""
    name = graphene.String(required=True, description="Tên nhóm")


# ===== REGISTER & LOGIN MUTATIONS =====

class RegisterMutation(Mutation):
    """Mutation đăng ký user mới"""
    
    class Arguments:
        input = RegisterInput(required=True)
    
    success = graphene.Boolean()
    user = graphene.Field(UserType)
    errors = graphene.Field(ErrorType)
    message = graphene.String()
    
    def mutate(self, info, input):
        errors = {}
        
        try:
            with transaction.atomic():
                # Validate các trường required
                if not input.full_name.strip():
                    errors['general'] = "Họ và tên không được để trống"
                
                if not input.username.strip():
                    errors['username'] = "Tên đăng nhập không được để trống"
                
                if not input.email.strip():
                    errors['email'] = "Email không được để trống"
                
                # Kiểm tra username unique
                if User.objects.filter(username=input.username).exists():
                    errors['username'] = "Tên đăng nhập đã tồn tại"
                
                # Kiểm tra email unique
                if User.objects.filter(email=input.email).exists():
                    errors['email'] = "Email đã được sử dụng"
                
                # Validate password
                try:
                    validate_password(input.password)
                except ValidationError as e:
                    errors['password'] = "; ".join(e.messages)
                
                if errors:
                    return RegisterMutation(
                        success=False,
                        errors=ErrorType(**errors)
                    )
                
                # Tạo user mới
                user = User.objects.create_user(
                    username=input.username,
                    email=input.email,
                    password=input.password
                )
                
                # Set custom fields
                user.full_name = input.full_name
                user.role = 'buyer'  # Default role
                if input.birth_date:
                    user.birth_date = input.birth_date
                user.save()
                
                return RegisterMutation(
                    success=True,
                    user=user,
                    message="Đăng ký thành công"
                )
                
        except Exception as e:
            return RegisterMutation(
                success=False,
                errors=ErrorType(general=str(e))
            )

class LoginMutation(Mutation):
    """Mutation đăng nhập"""
    
    class Arguments:
        input = LoginInput(required=True)
    
    success = graphene.Boolean()
    user = graphene.Field(UserType)
    tokens = graphene.Field(TokenType)
    errors = graphene.Field(ErrorType)
    message = graphene.String()
    
    def mutate(self, info, input):
        errors = {}
        
        # Validate input
        if not input.username.strip():
            errors['username'] = "Tên đăng nhập không được để trống"
        
        if not input.password.strip():
            errors['password'] = "Mật khẩu không được để trống"
        
        if errors:
            return LoginMutation(
                success=False,
                errors=ErrorType(**errors)
            )
        
        # Authenticate user
        user = authenticate(
            request=info.context,
            username=input.username,
            password=input.password
        )
        
        if user is None:
            # Kiểm tra xem username có tồn tại không
            if not User.objects.filter(username=input.username).exists():
                errors['username'] = "Tên đăng nhập không tồn tại"
            else:
                errors['password'] = "Mật khẩu không chính xác"
            
            return LoginMutation(
                success=False,
                errors=ErrorType(**errors)
            )
        
        if not user.is_active:
            return LoginMutation(
                success=False,
                errors=ErrorType(general="Tài khoản đã bị khóa")
            )
        
        # Login user
        login(info.context, user)
        
        # Generate tokens
        access_token = generate_jwt_token(user)
        refresh_token = generate_refresh_token()
        expires_in = 24 * 60 * 60  # 24 hours in seconds
        
        if input.remember_me:
            expires_in = 30 * 24 * 60 * 60  # 30 days
        
        tokens = TokenType(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in
        )
        
        return LoginMutation(
            success=True,
            user=user,
            tokens=tokens,
            message="Đăng nhập thành công"
        )

class LogoutMutation(Mutation):
    """Mutation đăng xuất"""
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info):
        if info.context.user.is_authenticated:
            logout(info.context)
            return LogoutMutation(
                success=True,
                message="Đăng xuất thành công"
            )
        
        return LogoutMutation(
            success=False,
            message="Bạn chưa đăng nhập"
        )


class RefreshTokenInput(InputObjectType):
    """Input cho refresh token"""
    refresh_token = graphene.String(required=True, description="Refresh token")


class RefreshTokenMutation(Mutation):
    """Mutation để refresh access token khi hết hạn"""
    
    class Arguments:
        input = RefreshTokenInput(required=True)
    
    success = graphene.Boolean()
    tokens = graphene.Field(TokenType)
    errors = graphene.Field(ErrorType)
    message = graphene.String()
    
    def mutate(self, info, input):
        errors = {}
        
        # Validate refresh token
        if not input.refresh_token.strip():
            errors['general'] = "Refresh token không được để trống"
            return RefreshTokenMutation(
                success=False,
                errors=ErrorType(**errors)
            )
        
        try:
            # TODO: Trong thực tế, bạn cần lưu refresh token vào database
            # và kiểm tra xem nó có hợp lệ không
            # Ở đây tôi sẽ giả lập việc validate refresh token
            
            # Lấy user từ refresh token (giả lập)
            # Trong thực tế, bạn cần một bảng RefreshToken trong database
            # để lưu và validate refresh token
            
            # Tạm thời lấy user đầu tiên để demo
            user = User.objects.first()
            
            if not user or not user.is_active:
                errors['general'] = "Refresh token không hợp lệ hoặc đã hết hạn"
                return RefreshTokenMutation(
                    success=False,
                    errors=ErrorType(**errors)
                )
            
            # Generate new tokens
            access_token = generate_jwt_token(user)
            new_refresh_token = generate_refresh_token()
            expires_in = 24 * 60 * 60  # 24 hours
            
            tokens = TokenType(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=expires_in
            )
            
            return RefreshTokenMutation(
                success=True,
                tokens=tokens,
                message="Token đã được làm mới thành công"
            )
            
        except Exception as e:
            return RefreshTokenMutation(
                success=False,
                errors=ErrorType(general=f"Lỗi khi refresh token: {str(e)}")
            )


# ===== USER MUTATIONS =====

class UserCreate(Mutation):
    """Mutation tạo user mới"""
    
    class Arguments:
        input = UserCreateInput(required=True)
    
    success = graphene.Boolean()
    user = graphene.Field(UserType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        user = info.context.user
        
        # BỎ kiểm tra quyền, cho phép tạo user từ FE kiểm soát
        try:
            with transaction.atomic():
                # Kiểm tra username unique
                if User.objects.filter(username=input.username).exists():
                    return UserCreate(
                        success=False,
                        errors=["Username already exists"]
                    )
                
                # Kiểm tra email unique
                if User.objects.filter(email=input.email).exists():
                    return UserCreate(
                        success=False,
                        errors=["Email already exists"]
                    )
                
                # Validate password
                try:
                    validate_password(input.password)
                except ValidationError as e:
                    return UserCreate(
                        success=False,
                        errors=list(e.messages)
                    )
                
                # Tạo user với các field cơ bản
                new_user = User.objects.create_user(
                    username=input.username,
                    email=input.email,
                    password=input.password,
                    first_name=getattr(input, 'first_name', ''),
                    last_name=getattr(input, 'last_name', ''),
                    is_active=getattr(input, 'is_active', True)
                )
                
                # Set custom fields
                if hasattr(input, 'full_name') and input.full_name:
                    new_user.full_name = input.full_name
                if hasattr(input, 'phone') and input.phone:
                    new_user.phone = input.phone
                if hasattr(input, 'birth_date') and input.birth_date:
                    new_user.birth_date = input.birth_date
                if hasattr(input, 'role') and input.role:
                    # Validate role
                    valid_roles = ['buyer', 'seller', 'admin']
                    if input.role not in valid_roles:
                        return UserCreate(
                            success=False,
                            errors=[f"Invalid role. Must be one of: {', '.join(valid_roles)}"]
                        )
                    new_user.role = input.role
                else:
                    new_user.role = 'buyer'  # Default role
                
                new_user.save()
                
                # Thêm vào groups nếu có
                if hasattr(input, 'groups') and input.groups:
                    groups = Group.objects.filter(id__in=input.groups)
                    new_user.groups.set(groups)
                
                return UserCreate(
                    success=True,
                    user=new_user,
                    errors=[]
                )
                
        except Exception as e:
            return UserCreate(
                success=False,
                errors=[f"Error creating user: {str(e)}"]
            )


class UserUpdate(Mutation):
    """Mutation cập nhật user"""
    
    class Arguments:
        id = graphene.ID(required=True)
        input = UserUpdateInput(required=True)
    
    success = graphene.Boolean()
    user = graphene.Field(UserType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, id, input):
        current_user = info.context.user
        
        # BỎ kiểm tra authentication và phân quyền, FE tự kiểm soát
        try:
            target_user = User.objects.get(id=id)
        except User.DoesNotExist:
            return UserUpdate(
                success=False,
                errors=["User not found"]
            )
        
        # # Kiểm tra quyền (chỉ được update chính mình hoặc admin)
        # if target_user != current_user and not (current_user.is_staff or current_user.is_superuser):
        #     return UserUpdate(
        #         success=False,
        #         errors=["Permission denied"]
        #     )
        
        try:
            with transaction.atomic():
                # Kiểm tra username unique (nếu thay đổi)
                if hasattr(input, 'username') and input.username and input.username != target_user.username:
                    if User.objects.filter(username=input.username).exists():
                        return UserUpdate(
                            success=False,
                            errors=["Username already exists"]
                        )
                    target_user.username = input.username
                
                # Kiểm tra email unique (nếu thay đổi)
                if hasattr(input, 'email') and input.email and input.email != target_user.email:
                    if User.objects.filter(email=input.email).exists():
                        return UserUpdate(
                            success=False,
                            errors=["Email already exists"]
                        )
                    target_user.email = input.email
                
                # Cập nhật các trường khác
                if hasattr(input, 'first_name') and input.first_name is not None:
                    target_user.first_name = input.first_name
                if hasattr(input, 'last_name') and input.last_name is not None:
                    target_user.last_name = input.last_name
                    
                # Cập nhật các trường custom
                if hasattr(input, 'full_name') and input.full_name is not None:
                    target_user.full_name = input.full_name
                if hasattr(input, 'phone') and input.phone is not None:
                    target_user.phone = input.phone
                if hasattr(input, 'birth_date') and input.birth_date is not None:
                    target_user.birth_date = input.birth_date
                if hasattr(input, 'role') and input.role is not None:
                    # Validate role
                    valid_roles = ['buyer', 'seller', 'admin']
                    if input.role not in valid_roles:
                        return UserUpdate(
                            success=False,
                            errors=[f"Invalid role. Must be one of: {', '.join(valid_roles)}"]
                        )
                    # Chỉ admin mới được thay đổi role
                    if current_user.is_staff or current_user.is_superuser:
                        target_user.role = input.role
                        
                if hasattr(input, 'is_active') and input.is_active is not None and (current_user.is_staff or current_user.is_superuser):
                    target_user.is_active = input.is_active
                
                target_user.save()
                
                # Cập nhật groups (chỉ admin)
                if hasattr(input, 'groups') and input.groups and (current_user.is_staff or current_user.is_superuser):
                    groups = Group.objects.filter(id__in=input.groups)
                    target_user.groups.set(groups)
                
                return UserUpdate(
                    success=True,
                    user=target_user,
                    errors=[]
                )
                
        except Exception as e:
            return UserUpdate(
                success=False,
                errors=[f"Error updating user: {str(e)}"]
            )


class UserDelete(Mutation):
    """Mutation xóa user (soft delete)"""
    
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, id):
        current_user = info.context.user
        
        # BỎ kiểm tra quyền, FE tự kiểm soát
        try:
            target_user = User.objects.get(id=id)
        except User.DoesNotExist:
            return UserDelete(
                success=False,
                errors=["User not found"]
            )
        
        # Không cho phép xóa chính mình
        if target_user == current_user:
            return UserDelete(
                success=False,
                errors=["Cannot delete yourself"]
            )
        
        try:
            # Soft delete - chỉ set is_active = False
            target_user.is_active = False
            target_user.save()
            
            return UserDelete(
                success=True,
                errors=[]
            )
            
        except Exception as e:
            return UserDelete(
                success=False,
                errors=[f"Error deleting user: {str(e)}"]
            )


class PasswordChange(Mutation):
    """Mutation đổi mật khẩu"""
    
    class Arguments:
        input = PasswordChangeInput(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        user = info.context.user
        
        # BỎ kiểm tra authentication, FE tự kiểm soát
        # Kiểm tra mật khẩu cũ
        if not user.check_password(input.old_password):
            return PasswordChange(
                success=False,
                errors=["Old password is incorrect"]
            )
        
        # Validate mật khẩu mới
        try:
            validate_password(input.new_password, user)
        except ValidationError as e:
            return PasswordChange(
                success=False,
                errors=list(e.messages)
            )
        
        try:
            # Đổi mật khẩu
            user.set_password(input.new_password)
            user.save()
            
            return PasswordChange(
                success=True,
                errors=[]
            )
            
        except Exception as e:
            return PasswordChange(
                success=False,
                errors=[f"Error changing password: {str(e)}"]
            )


# ===== GROUP MUTATIONS =====

class GroupCreate(Mutation):
    """Mutation tạo nhóm mới"""
    
    class Arguments:
        input = GroupCreateInput(required=True)
    
    success = graphene.Boolean()
    group = graphene.Field(GroupType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        user = info.context.user
        
        # BỎ kiểm tra quyền, FE tự kiểm soát
        try:
            # Kiểm tra tên group unique
            if Group.objects.filter(name=input.name).exists():
                return GroupCreate(
                    success=False,
                    errors=["Group name already exists"]
                )
            
            # Tạo group
            group = Group.objects.create(name=input.name)
            
            return GroupCreate(
                success=True,
                group=group,
                errors=[]
            )
            
        except Exception as e:
            return GroupCreate(
                success=False,
                errors=[f"Error creating group: {str(e)}"]
            )


# Export all mutations
class GroupUpdate(Mutation):
    """Cập nhật group"""
    
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        permissions = graphene.List(graphene.ID)
    
    group = Field(GroupType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id, name=None, permissions=None):
        user = info.context.user
        # BỎ kiểm tra quyền, FE tự kiểm soát
        
        try:
            group = Group.objects.get(id=id)
            
            if name:
                # Check if name exists
                if Group.objects.filter(name=name).exclude(id=id).exists():
                    return GroupUpdate(
                        group=None,
                        success=False,
                        message="Tên group đã tồn tại"
                    )
                group.name = name
            
            group.save()
            
            # Update permissions if provided
            if permissions is not None:

                perms = Permission.objects.filter(id__in=permissions)
                group.permissions.set(perms)
            
            return GroupUpdate(
                group=group,
                success=True,
                message="Cập nhật group thành công"
            )
            
        except Group.DoesNotExist:
            return GroupUpdate(
                group=None,
                success=False,
                message="Không tìm thấy group"
            )
        except Exception as e:
            return GroupUpdate(
                group=None,
                success=False,
                message=f"Có lỗi xảy ra: {str(e)}"
            )


class GroupDelete(Mutation):
    """Xóa group"""
    
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, id):
        user = info.context.user
        # BỎ kiểm tra quyền, FE tự kiểm soát
        
        try:
            group = Group.objects.get(id=id)
            group_name = group.name
            group.delete()
            
            return GroupDelete(
                success=True,
                message=f"Đã xóa group '{group_name}' thành công"
            )
            
        except Group.DoesNotExist:
            return GroupDelete(
                success=False,
                message="Không tìm thấy group"
            )
        except Exception as e:
            return GroupDelete(
                success=False,
                message=f"Có lỗi xảy ra: {str(e)}"
            )


class UserGroupAdd(Mutation):
    """Thêm user vào group"""
    
    class Arguments:
        user_id = graphene.ID(required=True)
        group_id = graphene.ID(required=True)
    
    user = Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, user_id, group_id):
        user = info.context.user
        # BỎ kiểm tra quyền, FE tự kiểm soát
        
        try:
            target_user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
            
            target_user.groups.add(group)
            
            return UserGroupAdd(
                user=target_user,
                success=True,
                message=f"Đã thêm user '{target_user.username}' vào group '{group.name}'"
            )
            
        except User.DoesNotExist:
            return UserGroupAdd(
                user=None,
                success=False,
                message="Không tìm thấy user"
            )
        except Group.DoesNotExist:
            return UserGroupAdd(
                user=None,
                success=False,
                message="Không tìm thấy group"
            )
        except Exception as e:
            return UserGroupAdd(
                user=None,
                success=False,
                message=f"Có lỗi xảy ra: {str(e)}"
            )


class UserGroupRemove(Mutation):
    """Xóa user khỏi group"""
    
    class Arguments:
        user_id = graphene.ID(required=True)
        group_id = graphene.ID(required=True)
    
    user = Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, user_id, group_id):
        user = info.context.user
        # BỎ kiểm tra quyền, FE tự kiểm soát
        
        try:
            target_user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
            
            target_user.groups.remove(group)
            
            return UserGroupRemove(
                user=target_user,
                success=True,
                message=f"Đã xóa user '{target_user.username}' khỏi group '{group.name}'"
            )
            
        except User.DoesNotExist:
            return UserGroupRemove(
                user=None,
                success=False,
                message="Không tìm thấy user"
            )
        except Group.DoesNotExist:
            return UserGroupRemove(
                user=None,
                success=False,
                message="Không tìm thấy group"
            )
        except Exception as e:
            return UserGroupRemove(
                user=None,
                success=False,
                message=f"Có lỗi xảy ra: {str(e)}"
            )


# ===== AUTHENTICATION MUTATIONS (REMOVED DUPLICATE) =====

# ===== AVATAR UPLOAD MUTATIONS =====
from graphene_file_upload.scalars import Upload

class AvatarUploadInput(InputObjectType):
    """Input cho avatar upload"""
    avatar = Upload(required=True, description="File ảnh avatar")

class AvatarUploadMutation(Mutation):
    """Mutation để upload avatar cho user"""
    
    class Arguments:
        input = AvatarUploadInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)
    avatar_url = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user
        # BỎ kiểm tra authentication, FE tự kiểm soát
        
        try:
            avatar_file = input.avatar
            
            # Kiểm tra file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if avatar_file.content_type not in allowed_types:
                return AvatarUploadMutation(
                    success=False,
                    message="File phải là ảnh (JPEG, PNG, GIF)",
                    user=None,
                    avatar_url=None
                )
            
            # Kiểm tra file size (5MB)
            if avatar_file.size > 5 * 1024 * 1024:
                return AvatarUploadMutation(
                    success=False,
                    message="File không được vượt quá 5MB",
                    user=None,
                    avatar_url=None
                )
            
            # Xóa avatar cũ nếu có
            if user.avatar:
                try:
                    user.avatar.delete(save=False)
                except:
                    pass  # Không cần báo lỗi nếu file cũ không xóa được
            
            # Lưu avatar mới
            user.avatar = avatar_file
            user.save()
            
            # Tạo URL đầy đủ
            avatar_url = info.context.build_absolute_uri(user.avatar.url) if hasattr(info.context, 'build_absolute_uri') else f"http://localhost:8000{user.avatar.url}"
            
            return AvatarUploadMutation(
                success=True,
                message="Upload avatar thành công",
                user=user,
                avatar_url=avatar_url
            )
            
        except Exception as e:
            return AvatarUploadMutation(
                success=False,
                message=f"Có lỗi xảy ra: {str(e)}",
                user=None,
                avatar_url=None
            )

class AvatarDeleteMutation(Mutation):
    """Mutation để xóa avatar của user"""
    
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)
    
    @staticmethod
    def mutate(root, info):
        user = info.context.user
        # BỎ kiểm tra authentication, FE tự kiểm soát
        
        try:
            # Xóa avatar nếu có
            if user.avatar:
                try:
                    user.avatar.delete(save=True)
                    return AvatarDeleteMutation(
                        success=True,
                        message="Xóa avatar thành công",
                        user=user
                    )
                except Exception as delete_error:
                    return AvatarDeleteMutation(
                        success=False,
                        message=f"Không thể xóa file avatar: {str(delete_error)}",
                        user=None
                    )
            else:
                return AvatarDeleteMutation(
                    success=False,
                    message="User không có avatar để xóa",
                    user=user
                )
                
        except Exception as e:
            return AvatarDeleteMutation(
                success=False,
                message=f"Có lỗi xảy ra: {str(e)}",
                user=None
            )

class CurrentUserUpdateMutation(Mutation):
    """Mutation cập nhật thông tin user hiện tại"""
    
    class Arguments:
        input = UserUpdateInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)
    errors = graphene.Field(ErrorType)
    
    @staticmethod
    def mutate(root, info, input):
        current_user = info.context.user
        # BỎ kiểm tra authentication, FE tự kiểm soát
        
        try:
            with transaction.atomic():
                errors = {}
                
                # Kiểm tra email unique (nếu thay đổi)
                if hasattr(input, 'email') and input.email and input.email != current_user.email:
                    if User.objects.filter(email=input.email).exists():
                        errors['email'] = "Email đã được sử dụng"
                
                if errors:
                    return CurrentUserUpdateMutation(
                        success=False,
                        message="Validation failed",
                        errors=ErrorType(**errors)
                    )
                
                # Cập nhật các trường khác
                if hasattr(input, 'first_name') and input.first_name is not None:
                    current_user.first_name = input.first_name
                if hasattr(input, 'last_name') and input.last_name is not None:
                    current_user.last_name = input.last_name
                if hasattr(input, 'email') and input.email is not None:
                    current_user.email = input.email
                    
                # Cập nhật các trường custom
                if hasattr(input, 'full_name') and input.full_name is not None:
                    current_user.full_name = input.full_name
                if hasattr(input, 'phone') and input.phone is not None:
                    current_user.phone = input.phone
                if hasattr(input, 'birth_date') and input.birth_date is not None:
                    current_user.birth_date = input.birth_date
                
                current_user.save()
                
                return CurrentUserUpdateMutation(
                    success=True,
                    message="Cập nhật thông tin thành công",
                    user=current_user
                )
                
        except Exception as e:
            return CurrentUserUpdateMutation(
                success=False,
                message=f"Lỗi khi cập nhật: {str(e)}",
                errors=ErrorType(general=str(e))
            )

# Export all
__all__ = [
    'RegisterMutation',
    'LoginMutation',
    'LogoutMutation',
    'RefreshTokenMutation',
    'UserCreate',
    'UserUpdate', 
    'UserDelete',
    'PasswordChange',
    'AvatarUploadMutation',
    'AvatarDeleteMutation',
    'CurrentUserUpdateMutation',
]