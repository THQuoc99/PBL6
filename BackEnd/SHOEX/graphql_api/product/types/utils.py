# utils.py
from decimal import Decimal
from django.utils import timezone
from discount.models import Voucher
from django.db.models import Q

def get_max_discount(product):
    today = timezone.now().date()
    vouchers = Voucher.objects.filter(
        Q(voucher_products__product=product) |
        Q(voucher_categories__category=product.category) |
        Q(voucher_stores__store=product.store),
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    ).distinct()

    max_discount = Decimal('0.0')
    for v in vouchers:
        if v.discount_type == 'percent':
            discount = v.discount_value
        else:  # fixed
            if product.base_price > 0:
                discount = (v.discount_value / product.base_price) * 100
            else:
                discount = Decimal('0.0')
        if discount > max_discount:
            max_discount = discount

    return float(max_discount)
