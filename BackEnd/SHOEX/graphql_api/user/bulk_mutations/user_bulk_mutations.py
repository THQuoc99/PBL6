import graphene
from graphene import ObjectType, Mutation, Field, List, String, Boolean, ID
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from ..types.user import UserType, GroupType

User = get_user_model()


class BulkUserCreateInput(graphene.InputObjectType):
    """Input cho bulk tạo users"""
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    first_name = graphene.String()
    last_name = graphene.String()
    full_name = graphene.String()
    phone = graphene.String()
    role = graphene.String()
    is_active = graphene.Boolean(default_value=True)
    is_staff = graphene.Boolean(default_value=False)
    groups = graphene.List(graphene.ID)


class BulkUserUpdateInput(graphene.InputObjectType):
    """Input cho bulk update users"""
    id = graphene.ID(required=True)
    username = graphene.String()
    email = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    full_name = graphene.String()
    phone = graphene.String()
    role = graphene.String()
    last_name = graphene.String()
    is_active = graphene.Boolean()
    is_staff = graphene.Boolean()
    groups = graphene.List(graphene.ID)


class BulkOperationResult(graphene.ObjectType):
    """Kết quả của bulk operation"""
    success = graphene.Boolean()
    message = graphene.String() 
    errors = graphene.List(graphene.String)
    processed_count = graphene.Int()
    failed_count = graphene.Int()


class BulkUserCreateResult(graphene.ObjectType):
    """Kết quả bulk tạo users"""
    users = graphene.List(UserType)
    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(graphene.String)
    created_count = graphene.Int()
    failed_count = graphene.Int()


class BulkUserUpdateResult(graphene.ObjectType):
    """Kết quả bulk update users"""
    users = graphene.List(UserType)
    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(graphene.String)
    updated_count = graphene.Int()
    failed_count = graphene.Int()


class BulkUserDelete(Mutation):
    """Xóa nhiều users"""
    
    class Arguments:
        user_ids = graphene.List(graphene.ID, required=True)
        hard_delete = graphene.Boolean(default_value=False)
    
    result = graphene.Field(BulkOperationResult)
    
    @staticmethod
    def mutate(root, info, user_ids, hard_delete=False):
        user = info.context.user
        if not user.is_authenticated:
            return BulkUserDelete(result=BulkOperationResult(
                success=False,
                message="Bạn cần đăng nhập để thực hiện thao tác này",
                errors=["Authentication required"],
                processed_count=0,
                failed_count=len(user_ids)
            ))
        
        # Chỉ admin mới được xóa users
        if not user.is_staff:
            return BulkUserDelete(result=BulkOperationResult(
                success=False,
                message="Bạn không có quyền thực hiện thao tác này",
                errors=["Permission denied"],
                processed_count=0,
                failed_count=len(user_ids)
            ))
        
        errors = []
        processed_count = 0
        
        try:
            with transaction.atomic():
                users_to_delete = User.objects.filter(id__in=user_ids)
                
                # Không cho phép xóa chính mình
                if user.id in [int(uid) for uid in user_ids]:
                    errors.append("Không thể xóa chính mình")
                    return BulkUserDelete(result=BulkOperationResult(
                        success=False,
                        message="Có lỗi trong quá trình xóa",
                        errors=errors,
                        processed_count=0,
                        failed_count=len(user_ids)
                    ))
                
                # Không cho phép xóa superuser khác
                superuser_count = users_to_delete.filter(is_superuser=True).count()
                if superuser_count > 0 and not user.is_superuser:
                    errors.append("Không thể xóa superuser")
                    return BulkUserDelete(result=BulkOperationResult(
                        success=False,
                        message="Có lỗi trong quá trình xóa",
                        errors=errors,
                        processed_count=0,
                        failed_count=len(user_ids)
                    ))
                
                if hard_delete:
                    # Hard delete - xóa hẳn khỏi database
                    processed_count = users_to_delete.count()
                    users_to_delete.delete()
                else:
                    # Soft delete - chỉ set is_active = False
                    processed_count = users_to_delete.update(is_active=False)
                
                return BulkUserDelete(result=BulkOperationResult(
                    success=True,
                    message=f"Đã xóa thành công {processed_count} users",
                    errors=[],
                    processed_count=processed_count,
                    failed_count=0
                ))
                
        except Exception as e:
            return BulkUserDelete(result=BulkOperationResult(
                success=False,
                message="Có lỗi trong quá trình xóa",
                errors=[str(e)],
                processed_count=0,
                failed_count=len(user_ids)
            ))


class BulkUserCreate(Mutation):
    """Tạo nhiều users"""
    
    class Arguments:
        users_data = graphene.List(BulkUserCreateInput, required=True)
    
    result = graphene.Field(BulkUserCreateResult)
    
    @staticmethod
    def mutate(root, info, users_data):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return BulkUserCreate(result=BulkUserCreateResult(
                users=[],
                success=False,
                message="Bạn không có quyền thực hiện thao tác này",
                errors=["Permission denied"],
                created_count=0,
                failed_count=len(users_data)
            ))
        
        created_users = []
        errors = []
        created_count = 0
        failed_count = 0
        
        try:
            with transaction.atomic():
                for user_data in users_data:
                    try:
                        # Validate required fields
                        if not user_data.username or not user_data.email or not user_data.password:
                            errors.append(f"Username, email và password là bắt buộc")
                            failed_count += 1
                            continue
                        
                        # Check if username exists
                        if User.objects.filter(username=user_data.username).exists():
                            errors.append(f"Username '{user_data.username}' đã tồn tại")
                            failed_count += 1
                            continue
                        
                        # Check if email exists
                        if User.objects.filter(email=user_data.email).exists():
                            errors.append(f"Email '{user_data.email}' đã tồn tại")
                            failed_count += 1
                            continue
                        
                        # Validate password
                        try:
                            validate_password(user_data.password)
                        except ValidationError as e:
                            errors.append(f"Password không hợp lệ cho {user_data.username}: {', '.join(e.messages)}")
                            failed_count += 1
                            continue
                        
                        # Validate role if provided
                        if hasattr(user_data, 'role') and user_data.role:
                            valid_roles = ['buyer', 'seller', 'admin']
                            if user_data.role not in valid_roles:
                                errors.append(f"Invalid role '{user_data.role}' for {user_data.username}. Must be one of: {', '.join(valid_roles)}")
                                failed_count += 1
                                continue
                        
                        # Create user data dict
                        create_data = {
                            'username': user_data.username,
                            'email': user_data.email,
                            'first_name': user_data.first_name or '',
                            'last_name': user_data.last_name or '',
                            'is_active': user_data.is_active if user_data.is_active is not None else True,
                            'is_staff': user_data.is_staff if user_data.is_staff is not None else False
                        }
                        
                        # Add custom fields
                        if hasattr(user_data, 'full_name') and user_data.full_name:
                            create_data['full_name'] = user_data.full_name
                        if hasattr(user_data, 'phone') and user_data.phone:
                            create_data['phone'] = user_data.phone
                        if hasattr(user_data, 'role') and user_data.role:
                            create_data['role'] = user_data.role
                        
                        # Create user
                        new_user = User.objects.create_user(password=user_data.password, **create_data)
                        
                        # Add to groups
                        if user_data.groups:
                            groups = Group.objects.filter(id__in=user_data.groups)
                            new_user.groups.set(groups)
                        
                        created_users.append(new_user)
                        created_count += 1
                        
                    except Exception as e:
                        errors.append(f"Lỗi tạo user {user_data.username}: {str(e)}")
                        failed_count += 1
                
                success = created_count > 0
                message = f"Đã tạo thành công {created_count} users"
                if failed_count > 0:
                    message += f", {failed_count} users thất bại"
                
                return BulkUserCreate(result=BulkUserCreateResult(
                    users=created_users,
                    success=success,
                    message=message,
                    errors=errors,
                    created_count=created_count,
                    failed_count=failed_count
                ))
                
        except Exception as e:
            return BulkUserCreate(result=BulkUserCreateResult(
                users=[],
                success=False,
                message="Có lỗi trong quá trình tạo users",
                errors=[str(e)],
                created_count=0,
                failed_count=len(users_data)
            ))


class BulkUserUpdate(Mutation):
    """Cập nhật nhiều users"""
    
    class Arguments:
        users_data = graphene.List(BulkUserUpdateInput, required=True)
    
    result = graphene.Field(BulkUserUpdateResult)
    
    @staticmethod
    def mutate(root, info, users_data):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return BulkUserUpdate(result=BulkUserUpdateResult(
                users=[],
                success=False,
                message="Bạn không có quyền thực hiện thao tác này",
                errors=["Permission denied"],
                updated_count=0,
                failed_count=len(users_data)
            ))
        
        updated_users = []
        errors = []
        updated_count = 0
        failed_count = 0
        
        try:
            with transaction.atomic():
                for user_data in users_data:
                    try:
                        target_user = User.objects.get(id=user_data.id)
                        
                        # Update fields if provided
                        if user_data.username is not None:
                            # Check username uniqueness
                            if User.objects.filter(username=user_data.username).exclude(id=target_user.id).exists():
                                errors.append(f"Username '{user_data.username}' đã tồn tại cho user ID {user_data.id}")
                                failed_count += 1
                                continue
                            target_user.username = user_data.username
                        
                        if user_data.email is not None:
                            # Check email uniqueness
                            if User.objects.filter(email=user_data.email).exclude(id=target_user.id).exists():
                                errors.append(f"Email '{user_data.email}' đã tồn tại cho user ID {user_data.id}")
                                failed_count += 1
                                continue
                            target_user.email = user_data.email
                        
                        if user_data.first_name is not None:
                            target_user.first_name = user_data.first_name
                        
                        if user_data.last_name is not None:
                            target_user.last_name = user_data.last_name
                        
                        # Update custom fields
                        if hasattr(user_data, 'full_name') and user_data.full_name is not None:
                            target_user.full_name = user_data.full_name
                        
                        if hasattr(user_data, 'phone') and user_data.phone is not None:
                            target_user.phone = user_data.phone
                        
                        if hasattr(user_data, 'role') and user_data.role is not None:
                            valid_roles = ['buyer', 'seller', 'admin']
                            if user_data.role not in valid_roles:
                                errors.append(f"Invalid role '{user_data.role}' for user ID {user_data.id}. Must be one of: {', '.join(valid_roles)}")
                                failed_count += 1
                                continue
                            target_user.role = user_data.role
                        
                        if user_data.is_active is not None:
                            target_user.is_active = user_data.is_active
                        
                        if user_data.is_staff is not None:
                            target_user.is_staff = user_data.is_staff
                        
                        target_user.save()
                        
                        # Update groups
                        if user_data.groups is not None:
                            groups = Group.objects.filter(id__in=user_data.groups)
                            target_user.groups.set(groups)
                        
                        updated_users.append(target_user)
                        updated_count += 1
                        
                    except User.DoesNotExist:
                        errors.append(f"Không tìm thấy user với ID {user_data.id}")
                        failed_count += 1
                    except Exception as e:
                        errors.append(f"Lỗi cập nhật user ID {user_data.id}: {str(e)}")
                        failed_count += 1
                
                success = updated_count > 0
                message = f"Đã cập nhật thành công {updated_count} users"
                if failed_count > 0:
                    message += f", {failed_count} users thất bại"
                
                return BulkUserUpdate(result=BulkUserUpdateResult(
                    users=updated_users,
                    success=success,
                    message=message,
                    errors=errors,
                    updated_count=updated_count,
                    failed_count=failed_count
                ))
                
        except Exception as e:
            return BulkUserUpdate(result=BulkUserUpdateResult(
                users=[],
                success=False,
                message="Có lỗi trong quá trình cập nhật users",
                errors=[str(e)],
                updated_count=0,
                failed_count=len(users_data)
            ))


class BulkUserActivate(Mutation):
    """Kích hoạt/vô hiệu hóa nhiều users"""
    
    class Arguments:
        user_ids = graphene.List(graphene.ID, required=True)
        is_active = graphene.Boolean(required=True)
    
    result = graphene.Field(BulkOperationResult)
    
    @staticmethod
    def mutate(root, info, user_ids, is_active):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            return BulkUserActivate(result=BulkOperationResult(
                success=False,
                message="Bạn không có quyền thực hiện thao tác này",
                errors=["Permission denied"],
                processed_count=0,
                failed_count=len(user_ids)
            ))
        
        try:
            with transaction.atomic():
                # Không cho phép thay đổi trạng thái của chính mình
                if user.id in [int(uid) for uid in user_ids]:
                    return BulkUserActivate(result=BulkOperationResult(
                        success=False,
                        message="Không thể thay đổi trạng thái của chính mình",
                        errors=["Cannot modify own status"],
                        processed_count=0,
                        failed_count=len(user_ids)
                    ))
                
                processed_count = User.objects.filter(
                    id__in=user_ids
                ).update(is_active=is_active)
                
                action = "kích hoạt" if is_active else "vô hiệu hóa"
                
                return BulkUserActivate(result=BulkOperationResult(
                    success=True,
                    message=f"Đã {action} thành công {processed_count} users",
                    errors=[],
                    processed_count=processed_count,
                    failed_count=0
                ))
                
        except Exception as e:
            return BulkUserActivate(result=BulkOperationResult(
                success=False,
                message="Có lỗi trong quá trình thực hiện",
                errors=[str(e)],
                processed_count=0,
                failed_count=len(user_ids)
            ))


# Export all
__all__ = [
    'BulkUserCreateInput',
    'BulkUserUpdateInput',
    'BulkOperationResult',
    'BulkUserCreateResult',
    'BulkUserUpdateResult',
    'BulkUserDelete',
    'BulkUserCreate',
    'BulkUserUpdate',
    'BulkUserActivate',
]