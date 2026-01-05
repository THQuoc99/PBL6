
import graphene
from graphene import relay
from django.db import transaction
from address.models import Address
from ..types import AddressType


class AddAddressMutation(relay.ClientIDMutation):
    """Thêm địa chỉ mới"""
    
    class Input:
        phone_number = graphene.String(description="Số điện thoại liên hệ")
        name = graphene.String(description="Tên người nhận hàng")
        province = graphene.String(required=True, description="Tỉnh/Thành phố")
        ward = graphene.String(required=True, description="Phường/Xã")
        hamlet = graphene.String(description="Thôn/Xóm (tùy chọn)")
        detail = graphene.String(required=True, description="Địa chỉ chi tiết")
        is_default = graphene.Boolean(description="Đặt làm mặc định")
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    address = graphene.Field(AddressType)
    
    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        user = info.context.user
        
        # Check authentication
        if not user or not user.is_authenticated:
            return AddAddressMutation(
                success=False,
                errors=["Vui lòng đăng nhập để thêm địa chỉ"],
                address=None
            )
        
        try:
            with transaction.atomic():
                # Nếu là địa chỉ đầu tiên hoặc được đánh dấu default
                is_default = input.get('is_default', False)
                if not Address.objects.filter(user=user).exists():
                    is_default = True  # Địa chỉ đầu tiên tự động là default
                
                # Tạo địa chỉ mới
                address = Address.objects.create(
                    user=user,
                    phone_number=input.get('phone_number', ''),
                    name=input.get('name', ''),
                    province=input['province'],
                    ward=input['ward'],
                    hamlet=input.get('hamlet', ''),
                    detail=input['detail'],
                    is_default=is_default
                )
                
                return AddAddressMutation(
                    success=True,
                    errors=[],
                    address=address
                )
                
        except Exception as e:
            return AddAddressMutation(
                success=False,
                errors=[f"Lỗi khi thêm địa chỉ: {str(e)}"],
                address=None
            )


class UpdateAddressMutation(relay.ClientIDMutation):
    """Cập nhật địa chỉ"""
    
    class Input:
        address_id = graphene.Int(required=True, description="ID địa chỉ")
        phone_number = graphene.String(description="Số điện thoại liên hệ")
        name = graphene.String(description="Tên người nhận hàng")
        province = graphene.String(description="Tỉnh/Thành phố")
        ward = graphene.String(description="Phường/Xã")
        hamlet = graphene.String(description="Thôn/Xóm")
        detail = graphene.String(description="Địa chỉ chi tiết")
        is_default = graphene.Boolean(description="Đặt làm mặc định")
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    address = graphene.Field(AddressType)
    
    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        user = info.context.user
        
        if not user or not user.is_authenticated:
            return UpdateAddressMutation(
                success=False,
                errors=["Vui lòng đăng nhập để cập nhật địa chỉ"],
                address=None
            )
        
        try:
            address = Address.objects.get(
                address_id=input['address_id'],
                user=user
            )
            
            # Update fields
            # Update fields
            if 'phone_number' in input:
                address.phone_number = input['phone_number']
            if 'name' in input:
                address.name = input['name']
            if 'province' in input:
                address.province = input['province']
            if 'ward' in input:
                address.ward = input['ward']      # <-- dòng này bị thiếu indent khi bạn paste
            if 'hamlet' in input:
                address.hamlet = input['hamlet']
            if 'detail' in input:
                address.detail = input['detail']
            if 'is_default' in input:
                address.is_default = input['is_default']
            address.save()
            
            return UpdateAddressMutation(
                success=True,
                errors=[],
                address=address
            )
            
        except Address.DoesNotExist:
            return UpdateAddressMutation(
                success=False,
                errors=["Không tìm thấy địa chỉ"],
                address=None
            )
        except Exception as e:
            return UpdateAddressMutation(
                success=False,
                errors=[f"Lỗi khi cập nhật: {str(e)}"],
                address=None
            )


class DeleteAddressMutation(relay.ClientIDMutation):
    """Xóa địa chỉ"""
    
    class Input:
        address_id = graphene.Int(required=True, description="ID địa chỉ")
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        user = info.context.user
        
        if not user or not user.is_authenticated:
            return DeleteAddressMutation(
                success=False,
                errors=["Vui lòng đăng nhập để xóa địa chỉ"]
            )
        
        try:
            address = Address.objects.get(
                address_id=input['address_id'],
                user=user
            )
            
            # Không cho xóa địa chỉ mặc định nếu còn địa chỉ khác
            if address.is_default and Address.objects.filter(user=user).count() > 1:
                return DeleteAddressMutation(
                    success=False,
                    errors=["Không thể xóa địa chỉ mặc định. Vui lòng đặt địa chỉ khác làm mặc định trước."]
                )
            
            address.delete()
            
            return DeleteAddressMutation(
                success=True,
                errors=[]
            )
            
        except Address.DoesNotExist:
            return DeleteAddressMutation(
                success=False,
                errors=["Không tìm thấy địa chỉ"]
            )
        except Exception as e:
            return DeleteAddressMutation(
                success=False,
                errors=[f"Lỗi khi xóa: {str(e)}"]
            )


class SetDefaultAddressMutation(relay.ClientIDMutation):
    """Đặt địa chỉ làm mặc định"""
    
    class Input:
        address_id = graphene.Int(required=True, description="ID địa chỉ")
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    address = graphene.Field(AddressType)
    
    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        user = info.context.user
        
        if not user or not user.is_authenticated:
            return SetDefaultAddressMutation(
                success=False,
                errors=["Vui lòng đăng nhập"],
                address=None
            )
        
        try:
            address = Address.objects.get(
                address_id=input['address_id'],
                user=user
            )
            
            address.set_as_default()
            
            return SetDefaultAddressMutation(
                success=True,
                errors=[],
                address=address
            )
            
        except Address.DoesNotExist:
            return SetDefaultAddressMutation(
                success=False,
                errors=["Không tìm thấy địa chỉ"],
                address=None
            )
        except Exception as e:
            return SetDefaultAddressMutation(
                success=False,
                errors=[f"Lỗi: {str(e)}"],
                address=None
            )