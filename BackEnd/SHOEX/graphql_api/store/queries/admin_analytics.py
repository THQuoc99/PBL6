"""
Admin Analytics Query - Platform-wide analytics for admin dashboard
"""
import graphene
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Q, F
from django.utils import timezone

from store.models import Store
from orders.models import Order, SubOrder
from products.models import Product, Category
from users.models import User


# ===================================================================
# ============================ TYPES ================================
# ===================================================================

class RevenueTrendItemType(graphene.ObjectType):
    month = graphene.String()
    revenue = graphene.Decimal()
    orders = graphene.Int()
    growth = graphene.Float()


class CategoryPerformanceType(graphene.ObjectType):
    name = graphene.String()
    sales = graphene.Decimal()
    orders = graphene.Int()


class RegionalDistributionType(graphene.ObjectType):
    region = graphene.String()
    value = graphene.Float()


class UserGrowthType(graphene.ObjectType):
    month = graphene.String()
    customers = graphene.Int()
    sellers = graphene.Int()


class KeyMetricsType(graphene.ObjectType):
    """Key performance metrics"""
    revenue_growth = graphene.Float()  # % growth
    average_order_value = graphene.Decimal()
    retention_rate = graphene.Float()  # %


class AdminAnalyticsDataType(graphene.ObjectType):
    revenue_trend = graphene.List(RevenueTrendItemType)
    category_performance = graphene.List(CategoryPerformanceType)
    regional_distribution = graphene.List(RegionalDistributionType)
    user_growth = graphene.List(UserGrowthType)
    key_metrics = graphene.Field(KeyMetricsType)


# ===================================================================
# ============================ QUERY ================================
# ===================================================================

class AdminAnalyticsQuery(graphene.ObjectType):
    admin_analytics = graphene.Field(
        AdminAnalyticsDataType,
        range=graphene.String(default_value='30d'),
        limit=graphene.Int(default_value=12),
        description="Platform-wide analytics for admin dashboard"
    )

    def resolve_admin_analytics(self, info, **kwargs):
        """
        Resolve platform-wide analytics data
        range: '7d', '30d', '90d', '1y'
        limit: number of data points (e.g., 12 months)
        """
        # Get parameters without shadowing built-in functions
        time_range = kwargs.get('range', '30d')
        limit = kwargs.get('limit', 12)
        
        # Parse range parameter
        days_map = {'7d': 7, '30d': 30, '90d': 90, '1y': 365}
        days = days_map.get(time_range, 30)

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # ===================================================================
        # Revenue Trend (by month for last 12 months)
        # ===================================================================
        revenue_trend = []
        month_labels = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12']
        
        for i in range(min(limit, 12)):
            month_end = end_date - timedelta(days=i*30)
            month_start = month_end - timedelta(days=30)
            
            # Orders in this month
            month_orders = SubOrder.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end,
                # shipment__status='completed'
            )
            
            # Calculate revenue
            revenue_agg = month_orders.aggregate(
                total=Sum('subtotal'),
                shipping=Sum('shipping_fee')
            )
            month_revenue = Decimal(str(revenue_agg['total'] or 0)) + Decimal(str(revenue_agg['shipping'] or 0))
            month_order_count = month_orders.count()
            
            # Calculate growth (compare to previous month)
            prev_month_end = month_start
            prev_month_start = prev_month_end - timedelta(days=30)
            prev_month_orders = SubOrder.objects.filter(
                created_at__gte=prev_month_start,
                created_at__lt=prev_month_end,
                # shipment__status='completed'
            )
            prev_revenue_agg = prev_month_orders.aggregate(
                total=Sum('subtotal'),
                shipping=Sum('shipping_fee')
            )
            prev_revenue = Decimal(str(prev_revenue_agg['total'] or 0)) + Decimal(str(prev_revenue_agg['shipping'] or 0))
            
            growth = 0.0
            if prev_revenue > 0:
                growth = float((month_revenue - prev_revenue) / prev_revenue * 100)
            
            revenue_trend.insert(0, RevenueTrendItemType(
                month=month_labels[11 - i],
                revenue=month_revenue,
                orders=month_order_count,
                growth=round(growth, 2)
            ))

        # ===================================================================
        # Category Performance (top 5 categories by sales)
        # ===================================================================
        category_performance = []
        
        try:
            # Aggregate by category from products
            from products.models import ProductVariant
            from orders.models import OrderItem
            
            # Get ALL order items (không filter thời gian để hiển thị top categories)
            order_items = OrderItem.objects.all().select_related('variant__product__category')
            
            print(f"📊 Total OrderItems found: {order_items.count()}")
            
            category_stats = {}
            skipped_items = 0
            
            for item in order_items:
                try:
                    variant = item.variant
                    if variant and variant.product and variant.product.category:
                        cat_name = variant.product.category.name
                        # Dùng giá của variant
                        item_total = Decimal(str(variant.price)) * item.quantity
                        
                        print(f"  Item {item.item_id}: {cat_name} - Price: {variant.price} x {item.quantity} = {item_total}")
                        
                        if cat_name not in category_stats:
                            category_stats[cat_name] = {'sales': Decimal('0'), 'orders': 0}
                        
                        category_stats[cat_name]['sales'] += item_total
                        category_stats[cat_name]['orders'] += 1
                    else:
                        skipped_items += 1
                        print(f"  ⚠️ Item {item.item_id}: Missing variant={variant}, product={variant.product if variant else None}, category={variant.product.category if (variant and variant.product) else None}")
                except Exception as e:
                    print(f"⚠️ Error processing OrderItem {item.item_id}: {e}")
                    import traceback
                    traceback.print_exc()
                    skipped_items += 1
                    continue
            
            print(f"📈 Categories found: {len(category_stats)}")
            print(f"⚠️ Skipped items (no variant/product/category): {skipped_items}")
            
            # Sort by sales and take top 5
            sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]['sales'], reverse=True)[:5]
            
            print(f"🏆 Top 5 categories: {[cat[0] for cat in sorted_categories]}")
            
            for cat_name, stats in sorted_categories:
                category_performance.append(CategoryPerformanceType(
                    name=cat_name,
                    sales=stats['sales'],
                    orders=stats['orders']
                ))
        except Exception as e:
            # If category aggregation fails, return empty list
            print(f"❌ Category performance error: {e}")
            import traceback
            traceback.print_exc()
            pass

        # ===================================================================
        # Regional Distribution (by city/province from addresses)
        # ===================================================================
        regional_distribution = []
        
        try:
            # Get orders with addresses in range
            orders_with_addresses = Order.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
                address__isnull=False
            ).select_related('address')
            
            # Count by city
            city_counts = {}
            total_orders = 0
            
            for order in orders_with_addresses:
                try:
                    city = order.address.city or 'Khác'
                    city_counts[city] = city_counts.get(city, 0) + 1
                    total_orders += 1
                except Exception:
                    continue
            
            # Convert to percentages
            if total_orders > 0:
                sorted_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                for city, count in sorted_cities:
                    percentage = round((count / total_orders) * 100, 1)
                    regional_distribution.append(RegionalDistributionType(
                        region=city,
                        value=float(percentage)
                    ))
        except Exception as e:
            print(f"Regional distribution error: {e}")
            pass

        # ===================================================================
        # User Growth (customers and sellers by month)
        # ===================================================================
        user_growth = []
        
        try:
            for i in range(min(limit, 12)):
                month_end = end_date - timedelta(days=i*30)
                month_start = month_end - timedelta(days=30)
                
                # New customers (buyers) in this month
                new_customers = User.objects.filter(
                    role='buyer',
                    date_joined__gte=month_start,
                    date_joined__lt=month_end
                ).count()
                
                # New sellers in this month
                new_sellers = User.objects.filter(
                    role='seller',
                    date_joined__gte=month_start,
                    date_joined__lt=month_end
                ).count()
                
                user_growth.insert(0, UserGrowthType(
                    month=month_labels[11 - i],
                    customers=new_customers,
                    sellers=new_sellers
                ))
        except Exception as e:
            print(f"User growth error: {e}")
            pass

        # ===================================================================
        # Key Metrics (platform-wide KPIs)
        # ===================================================================
        key_metrics = None
        try:
            # Calculate current month vs previous month for growth metrics
            current_month_start = end_date - timedelta(days=30)
            prev_month_start = current_month_start - timedelta(days=30)
            
            # Current month revenue
            current_revenue_agg = SubOrder.objects.filter(
                created_at__gte=current_month_start,
                created_at__lte=end_date
            ).aggregate(
                total=Sum('subtotal'),
                shipping=Sum('shipping_fee')
            )
            current_revenue = Decimal(str(current_revenue_agg['total'] or 0)) + Decimal(str(current_revenue_agg['shipping'] or 0))
            
            # Previous month revenue
            prev_revenue_agg = SubOrder.objects.filter(
                created_at__gte=prev_month_start,
                created_at__lt=current_month_start
            ).aggregate(
                total=Sum('subtotal'),
                shipping=Sum('shipping_fee')
            )
            prev_revenue = Decimal(str(prev_revenue_agg['total'] or 0)) + Decimal(str(prev_revenue_agg['shipping'] or 0))
            
            # Revenue growth %
            revenue_growth = 0.0
            if prev_revenue > 0:
                revenue_growth = float((current_revenue - prev_revenue) / prev_revenue * 100)
            
            # Average order value - ALL SubOrders (không filter thời gian)
            all_revenue_agg = SubOrder.objects.all().aggregate(
                total=Sum('subtotal'),
                shipping=Sum('shipping_fee')
            )
            all_revenue = Decimal(str(all_revenue_agg['total'] or 0)) + Decimal(str(all_revenue_agg['shipping'] or 0))
            total_orders = SubOrder.objects.all().count()
            
            avg_order_value = Decimal('0')
            if total_orders > 0:
                avg_order_value = all_revenue / total_orders
            
            # Retention rate (returning customers)
            total_customers = Order.objects.filter(
                created_at__gte=current_month_start,
                created_at__lte=end_date
            ).values('buyer').distinct().count()
            
            returning_customers = Order.objects.filter(
                created_at__gte=current_month_start,
                created_at__lte=end_date
            ).values('buyer').annotate(
                order_count=Count('order_id')
            ).filter(order_count__gt=1).count()
            
            retention_rate = 0.0
            if total_customers > 0:
                retention_rate = (returning_customers / total_customers) * 100
            
            key_metrics = KeyMetricsType(
                revenue_growth=round(revenue_growth, 1),
                average_order_value=avg_order_value,
                retention_rate=round(retention_rate, 1)
            )
        except Exception as e:
            print(f"Key metrics error: {e}")
            pass

        return AdminAnalyticsDataType(
            revenue_trend=revenue_trend,
            category_performance=category_performance,
            regional_distribution=regional_distribution,
            user_growth=user_growth,
            key_metrics=key_metrics
        )
