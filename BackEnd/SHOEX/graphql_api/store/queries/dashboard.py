import graphene
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Q
from django.utils import timezone

from store.models import Store
from orders.models import SubOrder
from products.models import Product


class DailyRevenueType(graphene.ObjectType):
    date = graphene.Date()
    label = graphene.String()
    value = graphene.Decimal()


class OrderStatusCountType(graphene.ObjectType):
    status = graphene.String()
    label = graphene.String()
    count = graphene.Int()
    color = graphene.String()


class StoreDashboardMetricsType(graphene.ObjectType):
    total_revenue_7d = graphene.Decimal()
    total_orders_7d = graphene.Int()
    total_products = graphene.Int()
    total_customers_7d = graphene.Int()


class StoreDashboardChartsType(graphene.ObjectType):
    revenue_by_day_7d = graphene.List(DailyRevenueType)
    orders_by_status = graphene.List(OrderStatusCountType)


class StoreDashboardType(graphene.ObjectType):
    store_id = graphene.ID()
    store_name = graphene.String()
    metrics = graphene.Field(StoreDashboardMetricsType)
    charts = graphene.Field(StoreDashboardChartsType)


class StoreDashboardQuery(graphene.ObjectType):
    store_dashboard = graphene.Field(
        StoreDashboardType,
        store_id=graphene.ID(required=True),
        days=graphene.Int(default_value=7),
        description="Dashboard metrics and charts for a store"
    )

    def resolve_store_dashboard(self, info, store_id, days=7):
        try:
            store = Store.objects.get(pk=store_id)
        except Store.DoesNotExist:
            return None

        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # SubOrders in date range
        suborders_in_range = SubOrder.objects.filter(
            store=store,
            created_at__gte=start_date,
            created_at__lte=end_date
        )

        # === METRICS ===
        # Total revenue: sum of (subtotal + shipping_fee) for completed suborders
        revenue_qs = suborders_in_range.filter(
            shipment__status='completed'
        ).aggregate(
            total=Sum('subtotal'),
            shipping=Sum('shipping_fee')
        )
        total_revenue = Decimal(str(revenue_qs['total'] or 0)) + Decimal(str(revenue_qs['shipping'] or 0))

        # Total orders count
        total_orders = suborders_in_range.count()

        # Total products
        total_products = Product.objects.filter(store=store, is_active=True).count()

        # Total unique customers (distinct buyer from orders)
        total_customers = suborders_in_range.values('order__buyer').distinct().count()

        metrics = StoreDashboardMetricsType(
            total_revenue_7d=total_revenue,
            total_orders_7d=total_orders,
            total_products=total_products,
            total_customers_7d=total_customers
        )

        # === CHARTS ===
        # Revenue by day (last 7 days)
        revenue_by_day = []
        weekday_labels = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']
        
        for i in range(days):
            day_date = (start_date + timedelta(days=i)).date()
            day_end = datetime.combine(day_date, datetime.max.time())
            day_start = datetime.combine(day_date, datetime.min.time())
            
            day_revenue_qs = SubOrder.objects.filter(
                store=store,
                created_at__gte=timezone.make_aware(day_start),
                created_at__lte=timezone.make_aware(day_end),
                shipment__status='completed'
            ).aggregate(
                total=Sum('subtotal'),
                shipping=Sum('shipping_fee')
            )
            day_revenue = Decimal(str(day_revenue_qs['total'] or 0)) + Decimal(str(day_revenue_qs['shipping'] or 0))
            
            # Label: T2, T3, ... CN
            weekday_idx = day_date.weekday()
            label = weekday_labels[(weekday_idx + 1) % 7]
            
            revenue_by_day.append(DailyRevenueType(
                date=day_date,
                label=label,
                value=day_revenue
            ))

        # Orders by shipment status
        status_mapping = {
            'pending': ('Chờ xác nhận', '#3B82F6'),
            'shipping': ('Đang giao', '#F59E0B'),
            'out_for_delivery': ('Chờ giao hàng', '#F59E0B'),
            'completed': ('Đã giao', '#10B981'),
            'cancelled': ('Đã hủy', '#EF4444'),
            'returned': ('Trả hàng', '#EF4444'),
        }

        orders_by_status = []
        for status, (label_vi, color) in status_mapping.items():
            count = suborders_in_range.filter(shipment__status=status).count()
            if count > 0:  # Only include statuses with orders
                orders_by_status.append(OrderStatusCountType(
                    status=status,
                    label=label_vi,
                    count=count,
                    color=color
                ))

        charts = StoreDashboardChartsType(
            revenue_by_day_7d=revenue_by_day,
            orders_by_status=orders_by_status
        )

        return StoreDashboardType(
            store_id=store.store_id,
            store_name=store.name,
            metrics=metrics,
            charts=charts
        )
