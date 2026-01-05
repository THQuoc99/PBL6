import graphene
from graphene_django import DjangoObjectType
from discount.models import Voucher, VoucherProduct, VoucherCategory, UserVoucher, OrderVoucher, VoucherStore


class VoucherType(DjangoObjectType):
    times_used = graphene.Int()

    class Meta:
        model = Voucher
        fields = "__all__"
    
    def resolve_times_used(self, info):
        # Fallback if not annotated
        if hasattr(self, 'times_used'):
            return self.times_used
        return self.order_vouchers.count()


class VoucherProductType(DjangoObjectType):
    class Meta:
        model = VoucherProduct
        fields = "__all__"


class VoucherCategoryType(DjangoObjectType):
    class Meta:
        model = VoucherCategory
        fields = "__all__"


class UserVoucherType(DjangoObjectType):
    class Meta:
        model = UserVoucher
        fields = "__all__"


class OrderVoucherType(DjangoObjectType):
    class Meta:
        model = OrderVoucher
        fields = "__all__"


class VoucherStoreType(DjangoObjectType):
    class Meta:
        model = VoucherStore
        fields = "__all__"
