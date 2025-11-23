from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Q, Case, When, Value, BooleanField
from django.db.models.functions import Coalesce
from products.models import Product

def get_base_product_queryset():
    """
    Trả về QuerySet Product cơ bản với:
    - tổng số đã bán (sold_count)
    - tổng số bán 30 ngày gần đây (sold_count_last_30)
    - trung bình rating 30 ngày gần đây (avg_rating_last_30)
    - cờ is_hot và is_new
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)

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
            avg_rating_last_30=Coalesce(
                Avg(
                    'variants__order_items__reviews__rating',
                    filter=Q(variants__order_items__order__created_at__gte=thirty_days_ago)
                ), 0.0
            )
        )\
        .annotate(
            is_hot=Case(
                When(sold_count_last_30__gte=50, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            is_new=Case(
                When(created_at__gte=thirty_days_ago, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
    return qs
