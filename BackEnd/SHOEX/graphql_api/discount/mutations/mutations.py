import graphene
from django.utils import timezone
from django.db.models import Q
from django.db import transaction
from decimal import Decimal

from discount.models import Voucher, UserVoucher, OrderVoucher, VoucherStore
from store.models import Store
from users.models import User
from orders.models import Order

from ..types import UserVoucherType,VoucherProductType,VoucherType,VoucherStoreType,VoucherCategoryType,OrderVoucherType        

import graphene

class VoucherInput(graphene.InputObjectType):
    code = graphene.String(required=True)
    type = graphene.String(required=False)
    discount_type = graphene.String(required=True)
    discount_value = graphene.Decimal(required=True) # SỬA
    max_discount = graphene.Decimal()                # SỬA
    min_order_amount = graphene.Decimal(required=True) # SỬA
    is_active = graphene.Boolean(required=False)
    start_date = graphene.Date(required=True)
    end_date = graphene.Date(required=True)
    per_user_limit = graphene.Int(required=True)


class UpdateVoucherInput(graphene.InputObjectType):
    # All fields optional for partial updates
    code = graphene.String(required=False)
    type = graphene.String(required=False)
    discount_type = graphene.String(required=False)
    discount_value = graphene.Decimal(required=False)
    max_discount = graphene.Decimal(required=False)
    min_order_amount = graphene.Decimal(required=False)
    is_active = graphene.Boolean(required=False)
    start_date = graphene.Date(required=False)
    end_date = graphene.Date(required=False)
    per_user_limit = graphene.Int(required=False)
class CreatePlatformVoucher(graphene.Mutation):
    class Arguments:
        data = VoucherInput(required=True)

    ok = graphene.Boolean()
    voucher = graphene.Field(VoucherType)

    def mutate(self, info, data):
        # Respect provided is_active if passed, otherwise default to True
        is_active = True
        try:
            if data.is_active is not None:
                is_active = data.is_active
        except Exception:
            pass

        voucher = Voucher.objects.create(
            code=data.code,
            type="platform",
            discount_type=data.discount_type,
            discount_value=data.discount_value,
            max_discount=data.max_discount,
            min_order_amount=data.min_order_amount,
            start_date=data.start_date,
            end_date=data.end_date,
            per_user_limit=data.per_user_limit,
            is_active=is_active
        )

        return CreatePlatformVoucher(ok=True, voucher=voucher)
class CreateStoreVoucher(graphene.Mutation):
    class Arguments:
        data = VoucherInput(required=True)
        store_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    voucher = graphene.Field(VoucherType)

    def mutate(self, info, data, store_id):
        store = Store.objects.get(pk=store_id)

        # Respect provided is_active if passed, otherwise default to True
        is_active = True
        try:
            if data.is_active is not None:
                is_active = data.is_active
        except Exception:
            pass

        voucher = Voucher.objects.create(
            code=data.code,
            type="store",
            discount_type=data.discount_type,
            discount_value=data.discount_value,
            max_discount=data.max_discount,
            min_order_amount=data.min_order_amount,
            start_date=data.start_date,
            end_date=data.end_date,
            per_user_limit=data.per_user_limit,
            is_active=is_active
        )

        VoucherStore.objects.create(
            voucher=voucher,
            store=store
        )

        return CreateStoreVoucher(ok=True, voucher=voucher)
class UpdateVoucher(graphene.Mutation):
    class Arguments:
        voucher_id = graphene.ID(required=True)
        data = UpdateVoucherInput(required=True)

    ok = graphene.Boolean()
    voucher = graphene.Field(VoucherType)

    def mutate(self, info, voucher_id, data):
        voucher = Voucher.objects.get(pk=voucher_id)

        # Only set attributes provided (skip None), so is_active can be toggled or left unchanged
        for field, value in data.items():
            if value is not None:
                setattr(voucher, field, value)

        voucher.save()

        return UpdateVoucher(ok=True, voucher=voucher)

class SaveVoucher(graphene.Mutation):
    class Arguments:
        voucher_id = graphene.ID(required=False)
        code = graphene.String(required=False)

    ok = graphene.Boolean()
    user_voucher = graphene.Field(UserVoucherType)
    message = graphene.String()

    def mutate(self, info, voucher_id=None, code=None):
        user = info.context.user
        if not user.is_authenticated:
            return SaveVoucher(ok=False, message="Vui lòng đăng nhập")
        # Accept either voucher_id or code. Prefer voucher_id when both provided.
        voucher = None
        # If voucher_id provided (not None/empty), try to fetch by PK
        if voucher_id:
            try:
                voucher = Voucher.objects.get(pk=voucher_id)
            except Voucher.DoesNotExist:
                return SaveVoucher(ok=False, message="Voucher không tồn tại (voucher_id)")
        else:
            # Fallback to code
            if code:
                try:
                    voucher = Voucher.objects.get(code=code)
                except Voucher.DoesNotExist:
                    return SaveVoucher(ok=False, message="Voucher không tồn tại (code)")
            else:
                return SaveVoucher(ok=False, message="Cần cung cấp voucher_id hoặc code")

        user_voucher, created = UserVoucher.objects.get_or_create(
            user=user,
            voucher=voucher
        )

        if created:
            return SaveVoucher(ok=True, user_voucher=user_voucher, message="Thành công")
        else:
            return SaveVoucher(ok=True, user_voucher=user_voucher, message="Bạn đã lưu voucher này rồi")


class ApplyVoucher(graphene.Mutation):
    class Arguments:
        voucher_code = graphene.String(required=True)
        order_total = graphene.Float(required=True)

    discount_amount = graphene.Float()
    message = graphene.String()

    def mutate(self, info, voucher_code, order_total):
        user = info.context.user
        if not user.is_authenticated:
            return ApplyVoucher(message="Vui lòng đăng nhập", discount_amount=0)

        try:
            voucher = Voucher.objects.get(code=voucher_code, is_active=True)
        except Voucher.DoesNotExist:
            return ApplyVoucher(message="Voucher không tồn tại", discount_amount=0)

        today = timezone.now().date()
        if not (voucher.start_date <= today <= voucher.end_date):
            return ApplyVoucher(message="Voucher hết hạn", discount_amount=0)

        # Min order
        if order_total < float(voucher.min_order_amount):
            return ApplyVoucher(message="Không đủ điều kiện đơn tối thiểu", discount_amount=0)

        # Lấy user voucher
        user_voucher, _ = UserVoucher.objects.get_or_create(user=user, voucher=voucher)

        if user_voucher.used_count >= voucher.per_user_limit:
            return ApplyVoucher(message="Bạn đã sử dụng hết số lần", discount_amount=0)

        # Tính giảm
        if voucher.discount_type == "fixed":
            discount = float(voucher.discount_value)
        elif voucher.discount_type == "percent":
            discount = order_total * (float(voucher.discount_value) / 100)
            if voucher.max_discount:
                discount = min(discount, float(voucher.max_discount))
        elif voucher.discount_type == "freeship":
            discount = float(voucher.discount_value)
        else:
            discount = 0

        return ApplyVoucher(
            message="Áp dụng thành công",
            discount_amount=discount,
        )
    
class DeleteVoucher(graphene.Mutation):
    class Arguments:
        voucher_id = graphene.ID(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, voucher_id):
        try:
            voucher = Voucher.objects.get(pk=voucher_id)
        except Voucher.DoesNotExist:
            return DeleteVoucher(ok=False, message="Voucher không tồn tại")

        # Xóa toàn bộ liên quan
        voucher.voucher_stores.all().delete()
        voucher.voucher_products.all().delete()
        voucher.voucher_categories.all().delete()
        voucher.user_vouchers.all().delete()
        voucher.order_vouchers.all().delete()

        voucher.delete()

        return DeleteVoucher(ok=True, message="Xóa voucher thành công")

class UseVoucher(graphene.Mutation):
    class Arguments:
        voucher_id = graphene.ID(required=True)
        order_id = graphene.ID(required=True)
        discount_amount = graphene.Float(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, voucher_id, order_id, discount_amount):
        user = info.context.user
        if not user.is_authenticated:
            return UseVoucher(ok=False, message="Vui lòng đăng nhập")

        try:
            with transaction.atomic():
                # Lock voucher row to avoid concurrent updates
                voucher = Voucher.objects.select_for_update().get(pk=voucher_id)
                try:
                    order = Order.objects.get(pk=order_id)
                except Order.DoesNotExist:
                    return UseVoucher(ok=False, message="Đơn hàng không tồn tại")

                # Idempotency: if this order already has this voucher recorded, return success
                if OrderVoucher.objects.filter(order=order, voucher=voucher).exists():
                    return UseVoucher(ok=True, message="Voucher đã được ghi nhận cho đơn này")

                user_voucher, created = UserVoucher.objects.get_or_create(
                    user=user,
                    voucher=voucher
                )

                # Lock the user_voucher row for update
                user_voucher = UserVoucher.objects.select_for_update().get(pk=user_voucher.pk)

                # Enforce per-user limit
                if voucher.per_user_limit is not None and user_voucher.used_count >= voucher.per_user_limit:
                    return UseVoucher(ok=False, message="Bạn đã sử dụng hết số lần")

                # Record usage
                user_voucher.used_count += 1

                # Decrement overall usage_limit if present and positive
                try:
                    if voucher.usage_limit is not None and voucher.usage_limit > 0:
                        voucher.usage_limit = max(voucher.usage_limit - 1, 0)
                except TypeError:
                    pass

                voucher.save()
                user_voucher.save()

                OrderVoucher.objects.create(
                    order=order,
                    voucher=voucher,
                    discount_amount=discount_amount
                )

                return UseVoucher(ok=True, message="Đã ghi nhận sử dụng voucher")
        except Voucher.DoesNotExist:
            return UseVoucher(ok=False, message="Voucher không tồn tại")
