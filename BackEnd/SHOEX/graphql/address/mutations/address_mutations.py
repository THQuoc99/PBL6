import graphene
from graphene_django.types import ErrorType
from django.db import transaction
from django.core.exceptions import ValidationError

from address.models import Province, Ward, Hamlet, Address
from users.models import User
from ..types.address import (
    ProvinceType, WardType, HamletType, AddressType,
    ProvinceInput, WardInput, HamletInput, AddressInput
)


class CreateProvince(graphene.Mutation):
    """Mutation để tạo tỉnh/thành phố mới"""
    
    class Arguments:
        input = ProvinceInput(required=True)
    
    province = graphene.Field(ProvinceType)
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, input):
        try:
            with transaction.atomic():
                province = Province.objects.create(
                    name=input.name
                )
                return CreateProvince(province=province)
        except ValidationError as e:
            return CreateProvince(errors=[ErrorType(message=str(e))])
        except Exception as e:
            return CreateProvince(errors=[ErrorType(message=f"Lỗi không xác định: {str(e)}")])


class UpdateProvince(graphene.Mutation):
    """Mutation để cập nhật tỉnh/thành phố"""
    
    class Arguments:
        id = graphene.ID(required=True)
        input = ProvinceInput(required=True)
    
    province = graphene.Field(ProvinceType)
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, id, input):
        try:
            with transaction.atomic():
                province = Province.objects.get(pk=id)
                province.name = input.name
                province.full_clean()
                province.save()
                return UpdateProvince(province=province)
        except Province.DoesNotExist:
            return UpdateProvince(errors=[ErrorType(message="Không tìm thấy tỉnh/thành phố")])
        except ValidationError as e:
            return UpdateProvince(errors=[ErrorType(message=str(e))])


class DeleteProvince(graphene.Mutation):
    """Mutation để xóa tỉnh/thành phố"""
    
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, id):
        try:
            with transaction.atomic():
                province = Province.objects.get(pk=id)
                province.delete()
                return DeleteProvince(success=True)
        except Province.DoesNotExist:
            return DeleteProvince(errors=[ErrorType(message="Không tìm thấy tỉnh/thành phố")])
        except Exception as e:
            return DeleteProvince(errors=[ErrorType(message=f"Không thể xóa: {str(e)}")])


class CreateWard(graphene.Mutation):
    """Mutation để tạo phường/xã mới"""
    
    class Arguments:
        input = WardInput(required=True)
    
    ward = graphene.Field(WardType)
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, input):
        try:
            with transaction.atomic():
                province = Province.objects.get(pk=input.province_id)
                ward = Ward.objects.create(
                    province=province,
                    name=input.name
                )
                return CreateWard(ward=ward)
        except Province.DoesNotExist:
            return CreateWard(errors=[ErrorType(message="Không tìm thấy tỉnh/thành phố")])
        except ValidationError as e:
            return CreateWard(errors=[ErrorType(message=str(e))])


class UpdateWard(graphene.Mutation):
    """Mutation để cập nhật phường/xã"""
    
    class Arguments:
        id = graphene.ID(required=True)
        input = WardInput(required=True)
    
    ward = graphene.Field(WardType)
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, id, input):
        try:
            with transaction.atomic():
                ward = Ward.objects.get(pk=id)
                province = Province.objects.get(pk=input.province_id)
                ward.province = province
                ward.name = input.name
                ward.full_clean()
                ward.save()
                return UpdateWard(ward=ward)
        except Ward.DoesNotExist:
            return UpdateWard(errors=[ErrorType(message="Không tìm thấy phường/xã")])
        except Province.DoesNotExist:
            return UpdateWard(errors=[ErrorType(message="Không tìm thấy tỉnh/thành phố")])
        except ValidationError as e:
            return UpdateWard(errors=[ErrorType(message=str(e))])


class DeleteWard(graphene.Mutation):
    """Mutation để xóa phường/xã"""
    
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, id):
        try:
            with transaction.atomic():
                ward = Ward.objects.get(pk=id)
                ward.delete()
                return DeleteWard(success=True)
        except Ward.DoesNotExist:
            return DeleteWard(errors=[ErrorType(message="Không tìm thấy phường/xã")])
        except Exception as e:
            return DeleteWard(errors=[ErrorType(message=f"Không thể xóa: {str(e)}")])


class CreateHamlet(graphene.Mutation):
    """Mutation để tạo thôn/xóm mới"""
    
    class Arguments:
        input = HamletInput(required=True)
    
    hamlet = graphene.Field(HamletType)
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, input):
        try:
            with transaction.atomic():
                ward = Ward.objects.get(pk=input.ward_id)
                hamlet = Hamlet.objects.create(
                    ward=ward,
                    name=input.name
                )
                return CreateHamlet(hamlet=hamlet)
        except Ward.DoesNotExist:
            return CreateHamlet(errors=[ErrorType(message="Không tìm thấy phường/xã")])
        except ValidationError as e:
            return CreateHamlet(errors=[ErrorType(message=str(e))])


class UpdateHamlet(graphene.Mutation):
    """Mutation để cập nhật thôn/xóm"""
    
    class Arguments:
        id = graphene.ID(required=True)
        input = HamletInput(required=True)
    
    hamlet = graphene.Field(HamletType)
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, id, input):
        try:
            with transaction.atomic():
                hamlet = Hamlet.objects.get(pk=id)
                ward = Ward.objects.get(pk=input.ward_id)
                hamlet.ward = ward
                hamlet.name = input.name
                hamlet.full_clean()
                hamlet.save()
                return UpdateHamlet(hamlet=hamlet)
        except Hamlet.DoesNotExist:
            return UpdateHamlet(errors=[ErrorType(message="Không tìm thấy thôn/xóm")])
        except Ward.DoesNotExist:
            return UpdateHamlet(errors=[ErrorType(message="Không tìm thấy phường/xã")])
        except ValidationError as e:
            return UpdateHamlet(errors=[ErrorType(message=str(e))])


class DeleteHamlet(graphene.Mutation):
    """Mutation để xóa thôn/xóm"""
    
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, id):
        try:
            with transaction.atomic():
                hamlet = Hamlet.objects.get(pk=id)
                hamlet.delete()
                return DeleteHamlet(success=True)
        except Hamlet.DoesNotExist:
            return DeleteHamlet(errors=[ErrorType(message="Không tìm thấy thôn/xóm")])
        except Exception as e:
            return DeleteHamlet(errors=[ErrorType(message=f"Không thể xóa: {str(e)}")])


class CreateAddress(graphene.Mutation):
    """Mutation để tạo địa chỉ mới"""
    
    class Arguments:
        input = AddressInput(required=True)
    
    address = graphene.Field(AddressType)
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, input):
        try:
            with transaction.atomic():
                user = User.objects.get(pk=input.user_id)
                province = Province.objects.get(pk=input.province_id)
                ward = Ward.objects.get(pk=input.ward_id)
                
                hamlet = None
                if input.hamlet_id:
                    hamlet = Hamlet.objects.get(pk=input.hamlet_id)
                
                address = Address.objects.create(
                    user=user,
                    province=province,
                    ward=ward,
                    hamlet=hamlet,
                    detail=input.detail,
                    is_default=input.is_default or False
                )
                return CreateAddress(address=address)
        except User.DoesNotExist:
            return CreateAddress(errors=[ErrorType(message="Không tìm thấy người dùng")])
        except Province.DoesNotExist:
            return CreateAddress(errors=[ErrorType(message="Không tìm thấy tỉnh/thành phố")])
        except Ward.DoesNotExist:
            return CreateAddress(errors=[ErrorType(message="Không tìm thấy phường/xã")])
        except Hamlet.DoesNotExist:
            return CreateAddress(errors=[ErrorType(message="Không tìm thấy thôn/xóm")])
        except ValidationError as e:
            return CreateAddress(errors=[ErrorType(message=str(e))])


class UpdateAddress(graphene.Mutation):
    """Mutation để cập nhật địa chỉ"""
    
    class Arguments:
        id = graphene.ID(required=True)
        input = AddressInput(required=True)
    
    address = graphene.Field(AddressType)
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, id, input):
        try:
            with transaction.atomic():
                address = Address.objects.get(pk=id)
                user = User.objects.get(pk=input.user_id)
                province = Province.objects.get(pk=input.province_id)
                ward = Ward.objects.get(pk=input.ward_id)
                
                hamlet = None
                if input.hamlet_id:
                    hamlet = Hamlet.objects.get(pk=input.hamlet_id)
                
                address.user = user
                address.province = province
                address.ward = ward
                address.hamlet = hamlet
                address.detail = input.detail
                if input.is_default is not None:
                    address.is_default = input.is_default
                
                address.full_clean()
                address.save()
                return UpdateAddress(address=address)
        except Address.DoesNotExist:
            return UpdateAddress(errors=[ErrorType(message="Không tìm thấy địa chỉ")])
        except User.DoesNotExist:
            return UpdateAddress(errors=[ErrorType(message="Không tìm thấy người dùng")])
        except Province.DoesNotExist:
            return UpdateAddress(errors=[ErrorType(message="Không tìm thấy tỉnh/thành phố")])
        except Ward.DoesNotExist:
            return UpdateAddress(errors=[ErrorType(message="Không tìm thấy phường/xã")])
        except Hamlet.DoesNotExist:
            return UpdateAddress(errors=[ErrorType(message="Không tìm thấy thôn/xóm")])
        except ValidationError as e:
            return UpdateAddress(errors=[ErrorType(message=str(e))])


class DeleteAddress(graphene.Mutation):
    """Mutation để xóa địa chỉ"""
    
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, id):
        try:
            with transaction.atomic():
                address = Address.objects.get(pk=id)
                address.delete()
                return DeleteAddress(success=True)
        except Address.DoesNotExist:
            return DeleteAddress(errors=[ErrorType(message="Không tìm thấy địa chỉ")])
        except Exception as e:
            return DeleteAddress(errors=[ErrorType(message=f"Không thể xóa: {str(e)}")])


class SetDefaultAddress(graphene.Mutation):
    """Mutation để đặt địa chỉ làm mặc định"""
    
    class Arguments:
        id = graphene.ID(required=True)
    
    address = graphene.Field(AddressType)
    errors = graphene.List(ErrorType)
    
    @classmethod
    def mutate(cls, root, info, id):
        try:
            with transaction.atomic():
                address = Address.objects.get(pk=id)
                address.set_as_default()
                return SetDefaultAddress(address=address)
        except Address.DoesNotExist:
            return SetDefaultAddress(errors=[ErrorType(message="Không tìm thấy địa chỉ")])
        except Exception as e:
            return SetDefaultAddress(errors=[ErrorType(message=f"Lỗi: {str(e)}")])


# Tổng hợp tất cả mutations
class AddressMutation(graphene.ObjectType):
    # Province mutations
    create_province = CreateProvince.Field()
    update_province = UpdateProvince.Field()
    delete_province = DeleteProvince.Field()
    
    # Ward mutations
    create_ward = CreateWard.Field()
    update_ward = UpdateWard.Field()
    delete_ward = DeleteWard.Field()
    
    # Hamlet mutations
    create_hamlet = CreateHamlet.Field()
    update_hamlet = UpdateHamlet.Field()
    delete_hamlet = DeleteHamlet.Field()
    
    # Address mutations
    create_address = CreateAddress.Field()
    update_address = UpdateAddress.Field()
    delete_address = DeleteAddress.Field()
    set_default_address = SetDefaultAddress.Field()