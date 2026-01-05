import graphene
from django.db.models import Q
from django.utils import timezone
from products.models import Product
from discount.models import Voucher, UserVoucher
from .types import VoucherType, UserVoucherType
from django.db import models 

class VoucherQuery(graphene.ObjectType):
    # 1. Voucher áp dụng cho product
    vouchers_for_product = graphene.List(
        VoucherType,
        product_id=graphene.ID(required=True)
    )

    # 1.5 Voucher dành cho một cửa hàng (store)
    vouchers_for_store = graphene.List(
        VoucherType,
        store_id=graphene.ID(required=False)
    )

    # 2. Voucher user đã lưu
    saved_vouchers = graphene.List(UserVoucherType)

    # 3. Voucher platform mà user chưa lưu
    available_platform_vouchers = graphene.List(VoucherType)
    # 4. Voucher phù hợp với đơn hàng
    all_applicable_vouchers = graphene.List(
        VoucherType,
        order_total=graphene.Float(required=True)
    )  

    def resolve_vouchers_for_product(self, info, product_id):
        today = timezone.now().date()
        product = Product.objects.get(pk=product_id)

        return Voucher.objects.filter(
            Q(voucher_products__product=product) |
            Q(voucher_categories__category=product.category) |
            Q(voucher_stores__store=product.store),
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).distinct()

    def resolve_vouchers_for_store(self, info, store_id=None):
        """Lấy danh sách voucher liên quan đến một cửa hàng.
        Nếu không truyền `store_id`, sẽ cố gắng lấy các store mà user là thành viên.
        """
        user = info.context.user
        today = timezone.now().date()

        if store_id:
            return Voucher.objects.filter(
                voucher_stores__store__store_id=store_id,
                start_date__lte=today,
                end_date__gte=today
            ).distinct()

        # Nếu không có store_id, lấy danh sách store từ membership của user
        if not user or not user.is_authenticated:
            return Voucher.objects.none()

        store_ids = user.store_memberships.values_list('store__store_id', flat=True)
        return Voucher.objects.filter(
            voucher_stores__store__store_id__in=store_ids,
            start_date__lte=today,
            end_date__gte=today
        ).distinct()

    def resolve_saved_vouchers(self, info):
        """Lấy danh sách voucher user đã lưu"""
        user = info.context.user
        if not user.is_authenticated:
            return []

        return UserVoucher.objects.filter(user=user).select_related("voucher")

    def resolve_available_platform_vouchers(self, info):
        """Lấy voucher platform mà user chưa lưu"""
        user = info.context.user
        if not user.is_authenticated:
            return Voucher.objects.none()

        today = timezone.now().date()

        saved_voucher_ids = UserVoucher.objects.filter(
            user=user
        ).values_list("voucher_id", flat=True)

        return Voucher.objects.filter(
            type="platform",
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).exclude(pk__in=saved_voucher_ids)
    def resolve_all_applicable_vouchers(self, info, order_total):
        user = info.context.user
        today = timezone.now().date()

        # 1. Voucher user đã lưu, còn hiệu lực, đủ điều kiện, chưa vượt quá số lần sử dụng
        user_voucher_qs = UserVoucher.objects.filter(
            user=user,
            voucher__is_active=True,
            voucher__start_date__lte=today,
            voucher__end_date__gte=today,
            voucher__min_order_amount__lte=order_total,
            used_count__lt=models.F('voucher__per_user_limit')
        ).select_related("voucher")

        user_vouchers = [uv.voucher for uv in user_voucher_qs]

        # 2. Voucher freeship còn hiệu lực trên toàn bảng
        freeship_vouchers = Voucher.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
            discount_type='freeship',
            min_order_amount__lte=order_total
        )
        all_vouchers = {v.voucher_id: v for v in user_vouchers}
        for v in freeship_vouchers:
            all_vouchers[v.voucher_id] = v

        return list(all_vouchers.values())
    
class VoucherMutations(graphene.ObjectType):
    from .mutations.mutations import (
        CreatePlatformVoucher,
        CreateStoreVoucher,
        UpdateVoucher,
        DeleteVoucher,
        SaveVoucher,
        ApplyVoucher,
        UseVoucher,
    )

    # PLATFORM + STORE
    create_platform_voucher = CreatePlatformVoucher.Field()
    create_store_voucher = CreateStoreVoucher.Field()
    # CRUD
    update_voucher = UpdateVoucher.Field()
    delete_voucher = DeleteVoucher.Field()
    # USER OPERATIONS
    save_voucher = SaveVoucher.Field()
    apply_voucher = ApplyVoucher.Field()
    use_voucher = UseVoucher.Field()
