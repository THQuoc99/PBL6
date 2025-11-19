# graphql_api/store/schema.py
import uuid
from django.utils import timezone
from django.utils.text import slugify

import graphene
from graphene import InputObjectType, Mutation, String, ID, Boolean, List
from graphene_file_upload.scalars import Upload
from graphene_django import DjangoObjectType

from store.models import Store, StoreUser, AddressStore
from django.contrib.auth import get_user_model

User = get_user_model()


# ===================================================================
# ============================ TYPES ================================
# ===================================================================

class StoreType(DjangoObjectType):
    class Meta:
        model = Store
        fields = "__all__"


class StoreUserType(DjangoObjectType):
    class Meta:
        model = StoreUser
        fields = "__all__"


class AddressStoreType(DjangoObjectType):
    class Meta:
        model = AddressStore
        fields = "__all__"


# ===================================================================
# ============================ INPUTS ===============================
# ===================================================================

class StoreUserInput(InputObjectType):
    store_id = String(required=True)
    user_id = String(required=True)
    role = String(required=True)
    status = String(required=False)
    granted_permissions = graphene.JSONString(required=False)
    revoked_permissions = graphene.JSONString(required=False)
    notes = String(required=False)


class AddressStoreInput(InputObjectType):
    store_id = String(required=True)
    province = String(required=True)
    ward = String(required=True)
    hamlet = String(required=False)
    detail = String(required=True)
    is_default = Boolean(required=False)


class StoreCreateInput(InputObjectType):
    name = String(required=True)
    email = String(required=False)
    phone = String(required=False)
    province = String(required=True)
    ward = String(required=True)
    hamlet = String(required=False)
    detail = String(required=True)


class StoreUpdateInput(InputObjectType):
    name = String()
    email = String()
    phone = String()
    currency = String()


# ===================================================================
# ============================ QUERY ================================
# ===================================================================

class StoreQuery(graphene.ObjectType):
    # Store
    store = graphene.Field(StoreType, store_id=ID(required=True))
    stores = List(StoreType)

    # Query MỚI: Lấy cửa hàng mà user là owner (chỉ 1 cái)
    my_owned_store = graphene.Field(
        StoreType,
        user_id=ID(required=False),
        description="Lấy cửa hàng duy nhất mà user là owner"
    )

    # Address Store
    address_store = graphene.Field(AddressStoreType, address_id=ID(required=True))
    address_stores = List(AddressStoreType, store_id=String(required=False))

    # Store User
    store_user = graphene.Field(StoreUserType, store_user_id=ID(required=True))
    store_users = List(StoreUserType, store_id=String(required=False), user_id=String(required=False))

    # ==================== RESOLVERS ====================

    def resolve_store(self, info, store_id):
        try:
            return Store.objects.get(store_id=store_id)
        except Store.DoesNotExist:
            return None

    def resolve_stores(self, info):
        return Store.objects.all().order_by('-created_at')

    # Resolver cho my_owned_store
    def resolve_my_owned_store(self, info, user_id=None):
        if user_id is None:
            if not info.context.user.is_authenticated:
                return None
            target_user = info.context.user
        else:
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return None

        membership = StoreUser.objects.filter(
            user=target_user,
            role='owner',
            status='active'
        ).select_related('store').first()

        return membership.store if membership else None

    # Address
    def resolve_address_store(self, info, address_id):
        try:
            return AddressStore.objects.get(address_id=address_id)
        except AddressStore.DoesNotExist:
            return None

    def resolve_address_stores(self, info, store_id=None):
        qs = AddressStore.objects.all()
        if store_id:
            qs = qs.filter(store__store_id=store_id)
        return qs.order_by('-is_default', 'address_id')

    # StoreUser
    def resolve_store_user(self, info, store_user_id):
        try:
            return StoreUser.objects.get(id=store_user_id)
        except StoreUser.DoesNotExist:
            return None

    def resolve_store_users(self, info, store_id=None, user_id=None):
        qs = StoreUser.objects.all()
        if store_id:
            qs = qs.filter(store__store_id=store_id)
        if user_id:
            qs = qs.filter(user__id=user_id)
        return qs.order_by('-created_at')


# ===================================================================
# ============================ MUTATIONS =============================
# ===================================================================

class CreateStoreUser(Mutation):
    class Arguments:
        input = StoreUserInput(required=True)

    success = Boolean()
    message = String()
    store_user = graphene.Field(StoreUserType)

    @staticmethod
    def mutate(root, info, input):
        try:
            store = Store.objects.get(store_id=input.store_id)
            user = User.objects.get(id=input.user_id)

            # Fix lỗi duplicate key
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
            )
            return CreateStoreUser(success=True, message="Thêm thành viên thành công", store_user=store_user)

        except Store.DoesNotExist:
            return CreateStoreUser(success=False, message="Không tìm thấy cửa hàng", store_user=None)
        except User.DoesNotExist:
            return CreateStoreUser(success=False, message="Không tìm thấy người dùng", store_user=None)
        except Exception as e:
            return CreateStoreUser(success=False, message=str(e), store_user=None)


class UpdateStoreUser(Mutation):
    class Arguments:
        store_user_id = ID(required=True)
        input = StoreUserInput(required=True)

    success = Boolean()
    message = String()
    store_user = graphene.Field(StoreUserType)

    @staticmethod
    def mutate(root, info, store_user_id, input):
        try:
            store_user = StoreUser.objects.get(id=store_user_id)
            store = Store.objects.get(store_id=input.store_id)
            user = User.objects.get(id=input.user_id)

            store_user.store = store
            store_user.user = user
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
            return UpdateStoreUser(success=True, message="Cập nhật thành công", store_user=store_user)
        except Exception as e:
            return UpdateStoreUser(success=False, message=str(e), store_user=None)


class DeleteStoreUser(Mutation):
    class Arguments:
        store_user_id = ID(required=True)

    success = Boolean()
    message = String()

    @staticmethod
    def mutate(root, info, store_user_id):
        try:
            store_user = StoreUser.objects.get(id=store_user_id)
            store_user.delete()
            return DeleteStoreUser(success=True, message="Xóa thành viên thành công")
        except StoreUser.DoesNotExist:
            return DeleteStoreUser(success=False, message="Không tìm thấy thành viên")


class CreateAddressStore(Mutation):
    class Arguments:
        input = AddressStoreInput(required=True)
    success = Boolean()
    message = String()
    address = graphene.Field(AddressStoreType)
    @staticmethod
    def mutate(root, info, input):
        try:
            store = Store.objects.get(store_id=input.store_id)
            address = AddressStore.objects.create(
                store=store,
                province=input.province,
                ward=input.ward,
                hamlet=getattr(input, "hamlet", "") or "",
                detail=input.detail,
                is_default=getattr(input, "is_default", False),
            )
            return CreateAddressStore(success=True, message="Tạo địa chỉ thành công", address=address)
        except Store.DoesNotExist:
            return CreateAddressStore(success=False, message="Không tìm thấy cửa hàng", address=None)


class UpdateAddressStore(Mutation):
    class Arguments:
        address_id = ID(required=True)
        input = AddressStoreInput(required=True)
    success = Boolean()
    message = String()
    address = graphene.Field(AddressStoreType)
    @staticmethod
    def mutate(root, info, address_id, input):
        try:
            address = AddressStore.objects.get(address_id=address_id)
            store = Store.objects.get(store_id=input.store_id)
            address.store = store
            address.province = input.province
            address.ward = input.ward
            address.hamlet = getattr(input, "hamlet", "") or ""
            address.detail = input.detail
            address.is_default = getattr(input, "is_default", False)
            address.save()
            return UpdateAddressStore(success=True, message="Cập nhật địa chỉ thành công", address=address)
        except (AddressStore.DoesNotExist, Store.DoesNotExist):
            return UpdateAddressStore(success=False, message="Không tìm thấy dữ liệu", address=None)


class DeleteAddressStore(Mutation):
    class Arguments:
        address_id = ID(required=True)
    success = Boolean()
    message = String()
    @staticmethod
    def mutate(root, info, address_id):
        try:
            address = AddressStore.objects.get(address_id=address_id)
            address.delete()
            return DeleteAddressStore(success=True, message="Xóa địa chỉ thành công")
        except AddressStore.DoesNotExist:
            return DeleteAddressStore(success=False, message="Không tìm thấy địa chỉ")


class CreateStore(Mutation):
    class Arguments:
        input = StoreCreateInput(required=True)
    success = Boolean()
    message = String()
    store = graphene.Field(StoreType)
    @staticmethod
    def mutate(root, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return CreateStore(success=False, message="Yêu cầu đăng nhập", store=None)

        store_id = uuid.uuid4().hex[:12]
        slug = slugify(input.name) or store_id

        store = Store.objects.create(
            store_id=store_id, name=input.name, slug=slug,
            email=input.email or "", phone=input.phone or "",
            address="", join_date=timezone.now(), currency="VND"
        )

        AddressStore.objects.create(
            store=store, province=input.province, ward=input.ward,
            hamlet=input.hamlet or "", detail=input.detail, is_default=True
        )

        StoreUser.objects.create(
            store=store, user=user, role="owner", status="active", joined_at=timezone.now()
        )

        return CreateStore(success=True, message="Tạo cửa hàng thành công", store=store)


class UpdateStore(Mutation):
    class Arguments:
        store_id = ID(required=True)
        input = StoreUpdateInput(required=True)
    success = Boolean()
    message = String()
    store = graphene.Field(StoreType)
    @staticmethod
    def mutate(root, info, store_id, input):
        try:
            store = Store.objects.get(store_id=store_id)
            if input.name is not None:
                store.name = input.name
                store.slug = slugify(input.name) or store.slug
            if input.email is not None: store.email = input.email
            if input.phone is not None: store.phone = input.phone
            if input.currency is not None: store.currency = input.currency
            store.save()
            return UpdateStore(success=True, message="Cập nhật thành công", store=store)
        except Store.DoesNotExist:
            return UpdateStore(success=False, message="Không tìm thấy cửa hàng", store=None)


class UpdateStoreImages(Mutation):
    class Arguments:
        store_id = ID(required=True)
        avatar = Upload(required=False)
        cover = Upload(required=False)
    success = Boolean()
    message = String()
    store = graphene.Field(StoreType)
    @staticmethod
    def mutate(root, info, store_id, avatar=None, cover=None):
        try:
            store = Store.objects.get(store_id=store_id)
            if avatar: store.avatar = avatar
            if cover: store.cover_image = cover
            store.save()
            return UpdateStoreImages(success=True, message="Cập nhật ảnh thành công", store=store)
        except Store.DoesNotExist:
            return UpdateStoreImages(success=False, message="Không tìm thấy cửa hàng", store=None)


# ===================================================================
# ========================== ALL MUTATIONS ==========================
# ===================================================================

class StoreMutation(graphene.ObjectType):
    create_store = CreateStore.Field()
    update_store = UpdateStore.Field()
    update_store_images = UpdateStoreImages.Field()

    create_address_store = CreateAddressStore.Field()
    update_address_store = UpdateAddressStore.Field()
    delete_address_store = DeleteAddressStore.Field()

    create_store_user = CreateStoreUser.Field()
    update_store_user = UpdateStoreUser.Field()
    delete_store_user = DeleteStoreUser.Field()