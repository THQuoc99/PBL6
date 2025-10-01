import graphene
from graphene import InputObjectType, Mutation, Field, String, Boolean, ID
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from ..types.user import UserType, GroupType

User = get_user_model()


# ===== INPUT TYPES =====

class UserCreateInput(InputObjectType):
    """Input cho tạo user mới"""
    username = graphene.String(required=True, description="Tên đăng nhập")
    email = graphene.String(required=True, description="Email")
    password = graphene.String(required=True, description="Mật khẩu")
    first_name = graphene.String(description="Họ")
    last_name = graphene.String(description="Tên")
    full_name = graphene.String(description="Họ và tên đầy đủ")
    phone = graphene.String(description="Số điện thoại")
    role = graphene.String(description="Vai trò: buyer, seller, admin")
    is_active = graphene.Boolean(default_value=True, description="Kích hoạt tài khoản")
    groups = graphene.List(graphene.ID, description="Danh sách ID nhóm")


class UserUpdateInput(InputObjectType):
    """Input cho cập nhật user"""
    username = graphene.String(description="Tên đăng nhập")
    email = graphene.String(description="Email")
    first_name = graphene.String(description="Họ")
    last_name = graphene.String(description="Tên")
    full_name = graphene.String(description="Họ và tên đầy đủ")
    phone = graphene.String(description="Số điện thoại")
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
        
        # Kiểm tra quyền (chỉ admin hoặc staff có thể tạo user)
        if not user.is_authenticated or not (user.is_staff or user.is_superuser):
            return UserCreate(
                success=False,
                errors=["Permission denied. Only staff can create users."]
            )
        
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
                
                # Tạo user
                user_data = {
                    'username': input.username,
                    'email': input.email,
                    'first_name': input.get('first_name', ''),
                    'last_name': input.get('last_name', ''),
                    'is_active': input.get('is_active', True)
                }
                
                # Thêm các trường custom nếu có
                if hasattr(input, 'full_name') and input.full_name:
                    user_data['full_name'] = input.full_name
                if hasattr(input, 'phone') and input.phone:
                    user_data['phone'] = input.phone
                if hasattr(input, 'role') and input.role:
                    # Validate role
                    valid_roles = ['buyer', 'seller', 'admin']
                    if input.role not in valid_roles:
                        return UserCreate(
                            success=False,
                            errors=[f"Invalid role. Must be one of: {', '.join(valid_roles)}"]
                        )
                    user_data['role'] = input.role
                
                new_user = User.objects.create_user(password=input.password, **user_data)
                
                # Thêm vào groups nếu có
                if input.get('groups'):
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
        
        # Kiểm tra authentication
        if not current_user.is_authenticated:
            return UserUpdate(
                success=False,
                errors=["Authentication required"]
            )
        
        try:
            target_user = User.objects.get(id=id)
        except User.DoesNotExist:
            return UserUpdate(
                success=False,
                errors=["User not found"]
            )
        
        # Kiểm tra quyền (chỉ được update chính mình hoặc admin)
        if target_user != current_user and not (current_user.is_staff or current_user.is_superuser):
            return UserUpdate(
                success=False,
                errors=["Permission denied"]
            )
        
        try:
            with transaction.atomic():
                # Kiểm tra username unique (nếu thay đổi)
                if input.get('username') and input.username != target_user.username:
                    if User.objects.filter(username=input.username).exists():
                        return UserUpdate(
                            success=False,
                            errors=["Username already exists"]
                        )
                    target_user.username = input.username
                
                # Kiểm tra email unique (nếu thay đổi)
                if input.get('email') and input.email != target_user.email:
                    if User.objects.filter(email=input.email).exists():
                        return UserUpdate(
                            success=False,
                            errors=["Email already exists"]
                        )
                    target_user.email = input.email
                
                # Cập nhật các trường khác
                if input.get('first_name') is not None:
                    target_user.first_name = input.first_name
                if input.get('last_name') is not None:
                    target_user.last_name = input.last_name
                    
                # Cập nhật các trường custom
                if hasattr(input, 'full_name') and input.full_name is not None:
                    target_user.full_name = input.full_name
                if hasattr(input, 'phone') and input.phone is not None:
                    target_user.phone = input.phone
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
                        
                if input.get('is_active') is not None and (current_user.is_staff or current_user.is_superuser):
                    target_user.is_active = input.is_active
                
                target_user.save()
                
                # Cập nhật groups (chỉ admin)
                if input.get('groups') and (current_user.is_staff or current_user.is_superuser):
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
        
        # Chỉ admin mới có thể xóa user
        if not current_user.is_authenticated or not (current_user.is_staff or current_user.is_superuser):
            return UserDelete(
                success=False,
                errors=["Permission denied. Only staff can delete users."]
            )
        
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
        
        if not user.is_authenticated:
            return PasswordChange(
                success=False,
                errors=["Authentication required"]
            )
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
        
        # Chỉ admin mới có thể tạo group
        if not user.is_authenticated or not (user.is_staff or user.is_superuser):
            return GroupCreate(
                success=False,
                errors=["Permission denied. Only staff can create groups."]
            )
        
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
        if not user.is_authenticated or not user.is_staff:
            return GroupUpdate(
                group=None,
                success=False,
                message="Bạn không có quyền thực hiện thao tác này"
            )
        
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
        if not user.is_authenticated or not user.is_staff:
            return GroupDelete(
                success=False,
                message="Bạn không có quyền thực hiện thao tác này"
            )
        
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
        if not user.is_authenticated or not user.is_staff:
            return UserGroupAdd(
                user=None,
                success=False,
                message="Bạn không có quyền thực hiện thao tác này"
            )
        
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
        if not user.is_authenticated or not user.is_staff:
            return UserGroupRemove(
                user=None,
                success=False,
                message="Bạn không có quyền thực hiện thao tác này"
            )
        
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


# ===== AUTHENTICATION MUTATIONS =====

class LoginMutation(graphene.Mutation):
    """Mutation đăng nhập"""
    class Arguments:
        username = graphene.String(required=True, description="Tên đăng nhập")
        password = graphene.String(required=True, description="Mật khẩu")

    success = graphene.Boolean(description="Trạng thái đăng nhập")
    message = graphene.String(description="Thông báo")
    user = Field(UserType, description="Thông tin user sau khi đăng nhập")

    def mutate(self, info, username, password):
        """Xử lý đăng nhập"""
        request = info.context
        user = authenticate(request, username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)  # Lưu vào session
                return LoginMutation(
                    success=True, 
                    message="Đăng nhập thành công",
                    user=user
                )
            else:
                return LoginMutation(
                    success=False, 
                    message="Tài khoản bị vô hiệu hóa",
                    user=None
                )
        
        return LoginMutation(
            success=False, 
            message="Sai tài khoản hoặc mật khẩu",
            user=None
        )


class LogoutMutation(graphene.Mutation):
    """Mutation đăng xuất"""
    success = graphene.Boolean(description="Trạng thái đăng xuất")
    message = graphene.String(description="Thông báo")

    def mutate(self, info):
        """Xử lý đăng xuất"""
        request = info.context
        if request.user.is_authenticated:
            logout(request)  # Xóa session
            return LogoutMutation(
                success=True,
                message="Đăng xuất thành công"
            )
        else:
            return LogoutMutation(
                success=False,
                message="Bạn chưa đăng nhập"
            )


# Export all
__all__ = [
    'UserCreateInput',
    'UserUpdateInput',
    'UserCreate',
    'UserUpdate',
    'UserDelete',
    'PasswordChange',
    'GroupCreate',
    'GroupUpdate',
    'GroupDelete',
    'UserGroupAdd',
    'UserGroupRemove',
    'LoginMutation',
    'LogoutMutation',
]