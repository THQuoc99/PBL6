from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Q, Case, When, Value, BooleanField, Min, Max, DecimalField, F
from django.db.models.functions import Coalesce
from products.models import Product

# ==== TIÊU CHUẨN ĐÁNH GIÁ SẢN PHẨM ====
DAYS_FOR_NEW = 30
HOT_SOLD_THRESHOLD = 50

def get_base_product_queryset():
    thirty_days_ago = timezone.now() - timedelta(days=DAYS_FOR_NEW)

    qs = Product.objects.filter(is_active=True)\
        .select_related("category", "store", "brand")\
        .prefetch_related("variants", "attribute_options")\
        .annotate(
            sold_count=Coalesce(Sum('variants__order_items__quantity'), 0),
            sold_count_last_30=Coalesce(
                Sum(
                    'variants__order_items__quantity',
                    filter=Q(variants__order_items__order__created_at__gte=thirty_days_ago)
                ), 0
            ),
            avg_rating=Coalesce(
                Avg('variants__order_items__reviews__rating'), 0.0
            )
        )\
        .annotate(
            is_hot=Case(
                When(sold_count_last_30__gte=HOT_SOLD_THRESHOLD, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            is_new=Case(
                When(created_at__gte=thirty_days_ago, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )\
        .annotate(
            # Annotate min/max price từ variants để có thể sort
            variant_min_price=Coalesce(
                Min('variants__price', filter=Q(variants__is_active=True)),
                F('base_price'),
                output_field=DecimalField()
            ),
            variant_max_price=Coalesce(
                Max('variants__price', filter=Q(variants__is_active=True)),
                F('base_price'),
                output_field=DecimalField()
            )
        )
    return qs