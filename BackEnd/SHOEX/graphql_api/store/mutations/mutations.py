import uuid
from django.utils import timezone
from django.utils.text import slugify
import graphene
from graphene import Mutation, Boolean, String, Field, ID
from graphene_file_upload.scalars import Upload
from django.contrib.auth import get_user_model

from store.models import Store, AddressStore, StoreUser
from ..types.types import StoreType, StoreUserType, AddressStoreType  # Sửa import này
from ..types.inputType import (  # Sửa import này
    StoreCreateInput,
    AddressStoreInput,
    StoreUserInput,
)

class CreateStore(Mutation):
    """Tạo Store mới"""
    class Arguments:
        input = StoreCreateInput(required=True)
        avatar = Upload()
        cover_image = Upload()
        logo = Upload()

    success = Boolean()
    message = String()
    store = Field(StoreType)

    @staticmethod
    def mutate(root, info, input, avatar=None, cover_image=None, logo=None):
        user = info.context.user
        if not user.is_authenticated:
            return CreateStore(success=False, message="Yêu cầu đăng nhập", store=None)

        # Kiểm tra user đã có store chưa
        existing_membership = StoreUser.objects.filter(
            user=user,
            role='owner',
            status='active'
        ).first()
        
        if existing_membership:
            return CreateStore(
                success=False,
                message="Bạn đã có một cửa hàng. Mỗi người chỉ được tạo một cửa hàng.",
                store=None
            )

        try:
            # Tạo store
            store_id = uuid.uuid4().hex[:12]
            slug = slugify(input.name) or store_id

            store = Store.objects.create(
                store_id=store_id,
                name=input.name,
                slug=slug,
                email=input.email or "",
                description=input.description or "",
                join_date=timezone.now(),
                currency="VND",
                timezone="Asia/Ho_Chi_Minh"
            )

            # Save uploaded images if provided
            if avatar:
                store.avatar = avatar
            if cover_image:
                store.cover_image = cover_image
            if logo:
                store.logo = logo
            store.save()
            # Create addresses if provided (supports list of AddressStoreInput)
            addresses_input = getattr(input, 'addresses', None)
            if addresses_input:
                # Only one default allowed. If multiple marked, only the first occurrence will be set.
                default_assigned = False
                valid_index = 0
                # First pass to find if any is marked default
                for a in addresses_input:
                    if (getattr(a, 'is_default', False) or (isinstance(a, dict) and a.get('is_default'))):
                        default_assigned = True
                        break
                default_assigned = False
                for idx, a in enumerate(addresses_input):
                    prov = getattr(a, 'province', None) or (a.get('province') if isinstance(a, dict) else None)
                    ward = getattr(a, 'ward', None) or (a.get('ward') if isinstance(a, dict) else None)
                    hamlet = getattr(a, 'hamlet', None) or (a.get('hamlet') if isinstance(a, dict) else "")
                    detail = getattr(a, 'detail', None) or (a.get('detail') if isinstance(a, dict) else None)
                    raw_is_def = (getattr(a, 'is_default', False) or (a.get('is_default') if isinstance(a, dict) else False))
                    phone = getattr(a, 'phone', None) or (a.get('phone') if isinstance(a, dict) else None)

                    # Skip incomplete address entries
                    if not prov or not ward or not detail:
                        continue

                    # Determine final is_default: prefer the first marked, otherwise first valid
                    is_def = False
                    if raw_is_def and not default_assigned:
                        is_def = True
                        default_assigned = True
                    elif not default_assigned and valid_index == 0:
                        # tentatively set first valid as default if none marked
                        is_def = True
                        default_assigned = True

                    valid_index += 1

                    AddressStore.objects.create(
                        store=store,
                        province=prov,
                        ward=ward,
                        hamlet=hamlet or "",
                        detail=detail,
                        is_default=bool(is_def),
                        phone=phone or ""
                    )
            else:
                # Backwards compatibility: if single address fields still present
                prov = getattr(input, 'province', None)
                ward = getattr(input, 'ward', None)
                detail = getattr(input, 'detail', None)
                hamlet = getattr(input, 'hamlet', None)
                if prov and ward and detail:
                    AddressStore.objects.create(
                        store=store,
                        province=prov,
                        ward=ward,
                        hamlet=hamlet or "",
                        detail=detail,
                        is_default=True
                    )

            # Tạo StoreUser với role owner
            StoreUser.objects.create(
                store=store,
                user=user,
                role="owner",
                status="active",
                joined_at=timezone.now()
            )

            return CreateStore(
                success=True,
                message="Tạo cửa hàng thành công",
                store=store
            )
        except Exception as e:
            return CreateStore(success=False, message=str(e), store=None)


class UpdateStore(Mutation):
    """Cập nhật thông tin Store (tương tự CreateStore)"""
    class Arguments:
        # prefer camelCase `storeId` only (remove legacy `store_id`)
        storeId = graphene.ID(required=False)
        input = StoreCreateInput(required=True)
        avatar = Upload()
        cover_image = Upload()
        logo = Upload()

    success = Boolean()
    message = String()
    store = Field(StoreType)

    @staticmethod
    def mutate(root, info, input, storeId=None, avatar=None, cover_image=None, logo=None):
        user = info.context.user
        if not user or not user.is_authenticated:
            return UpdateStore(success=False, message="Yêu cầu đăng nhập", store=None)

        # choose provided id
        chosen_store_id = storeId
        if not chosen_store_id:
            return UpdateStore(success=False, message="storeId là bắt buộc", store=None)

        try:
            store = Store.objects.get(store_id=chosen_store_id)

            # permission check
            membership = StoreUser.objects.filter(
                store=store,
                user=user,
                role__in=['owner', 'admin'],
                status='active'
            ).first()

            if not membership:
                return UpdateStore(success=False, message="Bạn không có quyền cập nhật cửa hàng này", store=None)

            # update basic fields (mirroring CreateStore inputs)
            if getattr(input, 'name', None) is not None:
                store.name = input.name
                store.slug = slugify(input.name) or store.slug

            if getattr(input, 'email', None) is not None:
                store.email = input.email or ""

            if getattr(input, 'description', None) is not None:
                store.description = input.description or ""

            # handle images
            if avatar:
                store.avatar = avatar
            if cover_image:
                store.cover_image = cover_image
            if logo:
                store.logo = logo

            store.save()

            # handle addresses if provided (supports list of AddressStoreInput)
            addresses_input = getattr(input, 'addresses', None)
            if addresses_input:
                # determine if any input marks default
                default_assigned = False
                for a in addresses_input:
                    if (getattr(a, 'is_default', False) or (isinstance(a, dict) and a.get('is_default'))):
                        default_assigned = True
                        break

                # process each address: update if address_id provided, else create
                for idx, a in enumerate(addresses_input):
                    addr_id = getattr(a, 'address_id', None) or (a.get('address_id') if isinstance(a, dict) else None)
                    prov = getattr(a, 'province', None) or (a.get('province') if isinstance(a, dict) else None)
                    ward = getattr(a, 'ward', None) or (a.get('ward') if isinstance(a, dict) else None)
                    hamlet = getattr(a, 'hamlet', None) or (a.get('hamlet') if isinstance(a, dict) else "")
                    detail = getattr(a, 'detail', None) or (a.get('detail') if isinstance(a, dict) else None)
                    raw_is_def = (getattr(a, 'is_default', False) or (a.get('is_default') if isinstance(a, dict) else False))
                    phone = getattr(a, 'phone', None) or (a.get('phone') if isinstance(a, dict) else None)

                    # Skip incomplete address entries
                    if not prov or not ward or not detail:
                        continue

                    is_def = bool(raw_is_def)

                    if addr_id:
                        try:
                            addr = AddressStore.objects.get(address_id=addr_id, store=store)
                            addr.province = prov
                            addr.ward = ward
                            addr.hamlet = hamlet or ""
                            addr.detail = detail
                            addr.phone = phone or ""
                            # set default only if marked
                            if is_def:
                                addr.is_default = True
                            addr.save()
                        except AddressStore.DoesNotExist:
                            # fall back to create if id not found
                            AddressStore.objects.create(
                                store=store,
                                province=prov,
                                ward=ward,
                                hamlet=hamlet or "",
                                detail=detail,
                                is_default=is_def,
                                phone=phone or ""
                            )
                    else:
                        AddressStore.objects.create(
                            store=store,
                            province=prov,
                            ward=ward,
                            hamlet=hamlet or "",
                            detail=detail,
                            is_default=is_def,
                            phone=phone or ""
                        )

                # Ensure only one default address per store: if any input marked default, clear others
                if default_assigned:
                    # find one marked in inputs (first occurrence)
                    chosen_default_id = None
                    for a in addresses_input:
                        if (getattr(a, 'is_default', False) or (isinstance(a, dict) and a.get('is_default'))):
                            chosen_default_id = getattr(a, 'address_id', None) or (a.get('address_id') if isinstance(a, dict) else None)
                            break

                    # set is_default appropriately
                    for addr in AddressStore.objects.filter(store=store):
                        if chosen_default_id and addr.address_id == chosen_default_id:
                            if not addr.is_default:
                                addr.is_default = True
                                addr.save(update_fields=['is_default'])
                        else:
                            if addr.is_default:
                                addr.is_default = False
                                addr.save(update_fields=['is_default'])

            return UpdateStore(success=True, message="Cập nhật thành công", store=store)
        except Store.DoesNotExist:
            return UpdateStore(success=False, message="Không tìm thấy cửa hàng", store=None)
        except Exception as e:
            return UpdateStore(success=False, message=str(e), store=None)

class UpdateStoreImages(Mutation):
    """Cập nhật ảnh Store"""
    class Arguments:
        store_id = graphene.ID(required=True)
        avatar = Upload()
        cover_image = Upload()
        logo = Upload()

    success = Boolean()
    message = String()
    store = Field(StoreType)

    @staticmethod
    def mutate(root, info, store_id, avatar=None, cover_image=None, logo=None):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateStoreImages(success=False, message="Yêu cầu đăng nhập", store=None)

        try:
            store = Store.objects.get(store_id=store_id)

            # Kiểm tra quyền
            membership = StoreUser.objects.filter(
                store=store,
                user=user,
                role__in=['owner', 'admin'],
                status='active'
            ).first()

            if not membership:
                return UpdateStoreImages(
                    success=False,
                    message="Bạn không có quyền cập nhật ảnh cửa hàng này",
                    store=None
                )

            if avatar:
                store.avatar = avatar
            if cover_image:
                store.cover_image = cover_image
            if logo:
                store.logo = logo

            store.save()

            return UpdateStoreImages(
                success=True,
                message="Cập nhật ảnh thành công",
                store=store
            )
        except Store.DoesNotExist:
            return UpdateStoreImages(success=False, message="Không tìm thấy cửa hàng", store=None)
        except Exception as e:
            return UpdateStoreImages(success=False, message=str(e), store=None)


class DeleteStore(Mutation):
    """Xóa Store (soft delete)"""
    class Arguments:
        store_id = graphene.ID(required=True)

    success = Boolean()
    message = String()

    @staticmethod
    def mutate(root, info, store_id):
        user = info.context.user
        if not user.is_authenticated:
            return DeleteStore(success=False, message="Yêu cầu đăng nhập")

        try:
            store = Store.objects.get(store_id=store_id)

            # Chỉ owner mới được xóa
            membership = StoreUser.objects.filter(
                store=store,
                user=user,
                role='owner',
                status='active'
            ).first()

            if not membership:
                return DeleteStore(
                    success=False,
                    message="Chỉ chủ cửa hàng mới được xóa cửa hàng"
                )

            # Soft delete
            store.is_active = False
            store.status = 'inactive'
            store.save()

            return DeleteStore(success=True, message="Xóa cửa hàng thành công")
        except Store.DoesNotExist:
            return DeleteStore(success=False, message="Không tìm thấy cửa hàng")
        except Exception as e:
            return DeleteStore(success=False, message=str(e))
        


class CreateAddressStore(Mutation):
    """Tạo địa chỉ mới cho Store"""
    class Arguments:
        store_id = graphene.String(required=True)
        input = AddressStoreInput(required=True)

    success = Boolean()
    message = String()
    address = Field(AddressStoreType)

    @staticmethod
    def mutate(root, info, store_id, input):
        user = info.context.user
        if not user.is_authenticated:
            return CreateAddressStore(success=False, message="Yêu cầu đăng nhập", address=None)

        try:
            store = Store.objects.get(store_id=store_id)

            # Kiểm tra quyền
            membership = StoreUser.objects.filter(
                store=store,
                user=user,
                role__in=['owner', 'admin', 'manager'],
                status='active'
            ).first()

            if not membership:
                return CreateAddressStore(
                    success=False,
                    message="Bạn không có quyền thêm địa chỉ cho cửa hàng này",
                    address=None
                )

            address = AddressStore.objects.create(
                store=store,
                province=input.province,
                ward=input.ward,
                hamlet=getattr(input, "hamlet", "") or "",
                detail=input.detail,
                is_default=getattr(input, "is_default", False),
                phone=getattr(input, 'phone', None) or ""
            )

            return CreateAddressStore(
                success=True,
                message="Tạo địa chỉ thành công",
                address=address
            )
        except Store.DoesNotExist:
            return CreateAddressStore(success=False, message="Không tìm thấy cửa hàng", address=None)
        except Exception as e:
            return CreateAddressStore(success=False, message=str(e), address=None)


class UpdateAddressStore(Mutation):
    """Cập nhật địa chỉ Store"""
    class Arguments:
        storeId = graphene.ID(required=False)
        input = AddressStoreInput(required=True)

    success = Boolean()
    message = String()
    address = Field(AddressStoreType)

    @staticmethod
    def mutate(root, info, input, storeId=None):
        user = info.context.user
        if not user or not user.is_authenticated:
            return UpdateAddressStore(success=False, message="Yêu cầu đăng nhập", address=None)

        try:
            # address_id should be provided inside input for updates
            address_id = getattr(input, 'address_id', None) or (input.get('address_id') if isinstance(input, dict) else None)
            if not address_id:
                return UpdateAddressStore(success=False, message="address_id là bắt buộc để cập nhật", address=None)

            address = AddressStore.objects.get(address_id=address_id)

            # if storeId provided, validate address belongs to the provided store
            if storeId:
                try:
                    provided_store = Store.objects.get(store_id=storeId)
                except Store.DoesNotExist:
                    return UpdateAddressStore(success=False, message="storeId không hợp lệ", address=None)
                # compare using the store_id string field (Store uses `store_id` as identifier)
                if getattr(address, 'store', None) is None or getattr(address.store, 'store_id', None) != getattr(provided_store, 'store_id', None):
                    return UpdateAddressStore(success=False, message="Địa chỉ không thuộc cửa hàng được cung cấp", address=None)

            # permission check against the existing address.store
            membership = StoreUser.objects.filter(
                store=address.store,
                user=user,
                role__in=['owner', 'admin', 'manager'],
                status='active'
            ).first()

            if not membership:
                return UpdateAddressStore(success=False, message="Bạn không có quyền cập nhật địa chỉ này", address=None)

            # update provided fields from input
            if getattr(input, 'province', None) is not None:
                address.province = input.province
            if getattr(input, 'ward', None) is not None:
                address.ward = input.ward
            if getattr(input, 'hamlet', None) is not None:
                address.hamlet = getattr(input, 'hamlet') or ""
            if getattr(input, 'detail', None) is not None:
                address.detail = input.detail
            if hasattr(input, 'is_default'):
                address.is_default = input.is_default
            if hasattr(input, 'phone'):
                address.phone = getattr(input, 'phone') or ""

            address.save()

            return UpdateAddressStore(success=True, message="Cập nhật địa chỉ thành công", address=address)
        except AddressStore.DoesNotExist:
            return UpdateAddressStore(success=False, message="Không tìm thấy địa chỉ", address=None)
        except Exception as e:
            return UpdateAddressStore(success=False, message=str(e), address=None)


class DeleteAddressStore(Mutation):
    """Xóa địa chỉ Store"""
    class Arguments:
        address_id = ID(required=True)

    success = Boolean()
    message = String()

    @staticmethod
    def mutate(root, info, address_id):
        user = info.context.user
        if not user.is_authenticated:
            return DeleteAddressStore(success=False, message="Yêu cầu đăng nhập")

        try:
            address = AddressStore.objects.get(address_id=address_id)
            
            # Kiểm tra quyền
            membership = StoreUser.objects.filter(
                store=address.store,
                user=user,
                role__in=['owner', 'admin', 'manager'],
                status='active'
            ).first()

            if not membership:
                return DeleteAddressStore(
                    success=False,
                    message="Bạn không có quyền xóa địa chỉ"
                )

            # Không cho xóa địa chỉ mặc định nếu còn địa chỉ khác
            if address.is_default:
                other_addresses = AddressStore.objects.filter(
                    store=address.store
                ).exclude(address_id=address_id)
                
                if other_addresses.exists():
                    return DeleteAddressStore(
                        success=False,
                        message="Vui lòng đặt địa chỉ khác làm mặc định trước khi xóa"
                    )

            address.delete()

            return DeleteAddressStore(success=True, message="Xóa địa chỉ thành công")
        except AddressStore.DoesNotExist:
            return DeleteAddressStore(success=False, message="Không tìm thấy địa chỉ")
        except Exception as e:
            return DeleteAddressStore(success=False, message=str(e))


class SetDefaultAddress(Mutation):
    """Đặt địa chỉ làm mặc định"""
    class Arguments:
        address_id = ID(required=True)

    success = Boolean()
    message = String()
    address = Field(AddressStoreType)

    @staticmethod
    def mutate(root, info, address_id):
        user = info.context.user
        if not user.is_authenticated:
            return SetDefaultAddress(success=False, message="Yêu cầu đăng nhập", address=None)

        try:
            address = AddressStore.objects.get(address_id=address_id)
            
            # Kiểm tra quyền
            membership = StoreUser.objects.filter(
                store=address.store,
                user=user,
                role__in=['owner', 'admin', 'manager'],
                status='active'
            ).first()

            if not membership:
                return SetDefaultAddress(
                    success=False,
                    message="Bạn không có quyền thay đổi địa chỉ mặc định",
                    address=None
                )

            address.set_as_default()

            return SetDefaultAddress(
                success=True,
                message="Đặt địa chỉ mặc định thành công",
                address=address
            )
        except AddressStore.DoesNotExist:
            return SetDefaultAddress(success=False, message="Không tìm thấy địa chỉ", address=None)
        except Exception as e:
            return SetDefaultAddress(success=False, message=str(e), address=None)

User = get_user_model()


class CreateStoreUser(Mutation):
    """Thêm thành viên vào Store"""
    class Arguments:
        input = StoreUserInput(required=True)

    success = Boolean()
    message = String()
    store_user = Field(StoreUserType)

    @staticmethod
    def mutate(root, info, input):
        user= info.context.user
        if not user.is_authenticated:
            return CreateStoreUser(success=False, message="Yêu cầu đăng nhập", store_user=None)

        try:
            store = Store.objects.get(store_id=input.store_id)

            # Kiểm tra quyền (chỉ owner/admin mới được thêm thành viên)
            membership = StoreUser.objects.filter(
                store=store,
                user=user,
                role__in=['owner', 'admin'],
                status='active'
            ).first()

            if not membership:
                return CreateStoreUser(
                    success=False,
                    message="Bạn không có quyền thêm thành viên",
                    store_user=None
                )

            # Kiểm tra duplicate
            if StoreUser.objects.filter(store=store, user=user).exists():
                return CreateStoreUser(
                    success=False,
                    message=f"User {user.username} đã là thành viên của cửa hàng này",
                    store_user=None
                )

            store_user = StoreUser.objects.create(
                store=store,
                user=user,
                role=input.role.lower(),
                status=getattr(input, "status", "pending") or "pending",
                granted_permissions=getattr(input, "granted_permissions", None),
                revoked_permissions=getattr(input, "revoked_permissions", None),
                notes=getattr(input, "notes", "") or "",
                invited_by=current_user
            )

            return CreateStoreUser(
                success=True,
                message="Thêm thành viên thành công",
                store_user=store_user
            )

        except Store.DoesNotExist:
            return CreateStoreUser(success=False, message="Không tìm thấy cửa hàng", store_user=None)
        except User.DoesNotExist:
            return CreateStoreUser(success=False, message="Không tìm thấy người dùng", store_user=None)
        except Exception as e:
            return CreateStoreUser(success=False, message=str(e), store_user=None)


class UpdateStoreUser(Mutation):
    """Cập nhật thông tin thành viên Store"""
    class Arguments:
        store_user_id = ID(required=True)
        input = StoreUserInput(required=True)

    success = Boolean()
    message = String()
    store_user = Field(StoreUserType)

    @staticmethod
    def mutate(root, info, store_user_id, input):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateStoreUser(success=False, message="Yêu cầu đăng nhập", store_user=None)

        try:
            store_user = StoreUser.objects.get(id=store_user_id)
            store = Store.objects.get(store_id=input.store_id)

            # Kiểm tra quyền
            membership = StoreUser.objects.filter(
                store=store,
                user=user,
                role__in=['owner', 'admin'],
                status='active'
            ).first()

            if not membership:
                return UpdateStoreUser(
                    success=False,
                    message="Bạn không có quyền cập nhật thành viên",
                    store_user=None
                )

            # Không cho thay đổi owner
            if store_user.role == 'owner' and input.role != 'owner':
                return UpdateStoreUser(
                    success=False,
                    message="Không thể thay đổi vai trò của chủ cửa hàng",
                    store_user=None
                )

            store_user.store = store
            # Không cập nhật user, chỉ cập nhật các trường khác
            store_user.role = input.role.lower()
            
            if input.status:
                store_user.status = input.status.lower()
            if input.granted_permissions is not None:
                store_user.granted_permissions = input.granted_permissions
            if input.revoked_permissions is not None:
                store_user.revoked_permissions = input.revoked_permissions
            if input.notes is not None:
                store_user.notes = input.notes

            store_user.save()

            return UpdateStoreUser(
                success=True,
                message="Cập nhật thành công",
                store_user=store_user
            )
        except Exception as e:
            return UpdateStoreUser(success=False, message=str(e), store_user=None)


class DeleteStoreUser(Mutation):
    """Xóa thành viên khỏi Store"""
    class Arguments:
        store_user_id = ID(required=True)

    success = Boolean()
    message = String()

    @staticmethod
    def mutate(root, info, store_user_id):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return DeleteStoreUser(success=False, message="Yêu cầu đăng nhập")

        try:
            store_user = StoreUser.objects.get(id=store_user_id)

            # Kiểm tra quyền
            membership = StoreUser.objects.filter(
                store=store_user.store,
                user=current_user,
                role__in=['owner', 'admin'],
                status='active'
            ).first()

            if not membership:
                return DeleteStoreUser(
                    success=False,
                    message="Bạn không có quyền xóa thành viên"
                )

            # Không cho xóa owner
            if store_user.role == 'owner':
                return DeleteStoreUser(
                    success=False,
                    message="Không thể xóa chủ cửa hàng"
                )

            store_user.delete()

            return DeleteStoreUser(success=True, message="Xóa thành viên thành công")
        except StoreUser.DoesNotExist:
            return DeleteStoreUser(success=False, message="Không tìm thấy thành viên")
        except Exception as e:
            return DeleteStoreUser(success=False, message=str(e))