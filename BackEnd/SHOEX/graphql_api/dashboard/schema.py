import graphene
from graphene import ObjectType, String, Field, List, Int, Float, Boolean, ID
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .types import DashboardStats, RevenueData, TopStore, CategoryData, RecentActivity, AdminStoreType, AdminUserType, AdminOrderType, AdminProductType, AdminAnalyticsType
from orders.models import Order, SubOrder
from store.models import Store, StoreUser
from django.contrib.auth import get_user_model
from products.models import Product, Category
from address.models import Address
from discount.models import Voucher

User = get_user_model()

class DashboardQuery(graphene.ObjectType):
    admin_dashboard = Field(DashboardStats)
    admin_stores = List(AdminStoreType)
    admin_users = List(AdminUserType)
    admin_orders = List(AdminOrderType)
    admin_products = List(AdminProductType)
    admin_analytics = Field(AdminAnalyticsType, range=graphene.String(), limit=graphene.Int())
    admin_vouchers = List('graphql_api.discount.types.VoucherType')
    admin_voucher_by_id = graphene.Field('graphql_api.discount.types.VoucherType', voucher_id=graphene.ID(required=True))
    admin_users = graphene.List(AdminUserType)

    def resolve_admin_dashboard(self, info):
        user = info.context.user
        # 1. Total Stats
        total_orders = Order.objects.count()
        # Revenue: Sum of subtotal of all SubOrders (since SubOrder represents actual store revenue)
        total_revenue_agg = SubOrder.objects.aggregate(Sum('subtotal'))
        total_revenue = total_revenue_agg['subtotal__sum'] or 0
        
        total_stores = Store.objects.count()
        total_users = User.objects.count()

        # 2. Revenue Last 30 Days
        revenue_data = []
        today = timezone.now().date()
        for i in range(29, -1, -1):
            date = today - timedelta(days=i)
            # Filter suborders created on this date
            day_orders = SubOrder.objects.filter(created_at__date=date)
            # Use 'subtotal' instead of 'total_amount'
            rev = day_orders.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
            cnt = day_orders.count()
            revenue_data.append(RevenueData(
                day=date.strftime("%d/%m"),
                revenue=float(rev),
                orders=cnt
            ))

        # 3. Top Stores (by revenue)
        # Identify top 5 stores based on suborders subtotal
        top_stores_qs = Store.objects.annotate(
            revenue=Sum('sub_orders__subtotal'),
            order_count=Count('sub_orders')
        ).order_by('-revenue')[:5]
        
        top_stores = []
        for s in top_stores_qs:
            top_stores.append(TopStore(
                name=s.name,
                revenue=float(s.revenue or 0),
                orders=s.order_count,
                # Rating is possibly a field or calculated. defaulting to 5.0 if not found
                rating=getattr(s, 'rating', 5.0) 
            ))

        # 4. Product by Category
        # Limitation: Just taking top 5 categories by product count
        categories = Category.objects.annotate(
            count=Count('products')
        ).order_by('-count')[:5]
        
        cat_data = []
        colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6']
        for i, cat in enumerate(categories):
            cat_data.append(CategoryData(
                name=cat.name,
                value=cat.count,
                color=colors[i % len(colors)]
            ))

        # 5. Recent Activities (Mocking some real data from latest orders/users)
        activities = []
        # Latest 2 orders
        latest_orders = Order.objects.order_by('-created_at')[:2]
        for o in latest_orders:
            activities.append(RecentActivity(
                id=o.pk,
                type='order',
                text=f"New order #{o.pk}",
                time=o.created_at.strftime("%H:%M"),
                status='success'
            ))
            
        # Latest 2 users
        latest_users = User.objects.order_by('-date_joined')[:2]
        for u in latest_users:
            activities.append(RecentActivity(
                id=u.pk,
                type='user',
                text=f"New user registered: {u.username}",
                time=u.date_joined.strftime("%H:%M"),
                status='info'
            ))

        return DashboardStats(
            total_revenue=float(total_revenue),
            total_orders=total_orders,
            total_stores=total_stores,
            total_users=total_users,
            revenue_by_day=revenue_data,
            top_stores=top_stores,
            product_by_category=cat_data,
            recent_activities=activities
        )

    def resolve_admin_stores(self, info):
        """Resolve list of all stores with aggregated stats"""
        # Note: No permission check as requested by user ("tạm thời ai cũng được")
        
        # Get all stores with aggregated revenue and order count
        qs = Store.objects.annotate(
            revenue=Sum('sub_orders__subtotal'),
            order_count=Count('sub_orders'),
            product_count=Count('products')
        )

        results = []
        for s in qs:
            # Attempt to find owner (StoreUser with role owner)
            # This might be N+1 query, but acceptable for admin panel with pagination (though here we return all)
            # If performance becomes issue, we can prefetch
            owner_name = "Unknown"
            owner_phone = ""
            owner_email = ""
            
            try:
                # Find the owner user
                owner_relation = StoreUser.objects.filter(store=s, role='owner').select_related('user').first()
                if owner_relation and owner_relation.user:
                    u = owner_relation.user
                    owner_name = u.get_full_name() or u.username
                    owner_email = u.email
                    owner_phone = getattr(u, 'phone', '') or '' # Assuming phone might be on profile or user model
            except Exception:
                pass
            
            # Address: take first address of store
            store_address = "N/A"
            try:
                addr = s.addresses.filter(is_default=True).first() or s.addresses.first()
                if addr:
                    store_address = f"{addr.city_province}" # Just displaying City/Province as in mock
            except Exception:
                pass
                
            results.append(AdminStoreType(
                id=s.store_id,
                name=s.name,
                owner_name=owner_name,
                email=owner_email or "N/A",
                phone=owner_phone or "N/A",
                address=store_address,
                status='active' if s.is_active else 'suspended', # Simple mapping for now
                revenue=float(s.revenue or 0),
                orders=s.order_count,
                products=s.product_count,
                rating=getattr(s, 'rating', 5.0),
                join_date=s.created_at.strftime("%Y-%m-%d"),
                avatar=s.avatar.url if s.avatar else ""
            ))
            
        return results

    def resolve_admin_users(self, info):
        """Resolve list of all users with aggregated stats"""
        # No permission check as requested
        
        users = User.objects.all().order_by('-date_joined')
        results = []
        
        for u in users:
            # Determine role
            role = 'customer'
            store_name = ""
            
            if u.is_superuser or u.is_staff:
                role = 'admin'
            else:
                # Check if seller
                store_ownership = StoreUser.objects.filter(user=u, role='owner').first()
                if store_ownership:
                    role = 'seller'
                    store_name = store_ownership.store.name
            
            # Determine status
            status = 'active' if u.is_active else 'banned'
            
            # Aggregate stats
            # Orders: Count of Orders where user is the customer
            orders_count = Order.objects.filter(buyer=u).count()
            
            # Spending: Sum of total_amount of Orders
            spending_agg = Order.objects.filter(buyer=u).aggregate(total=Sum('total_amount'))
            spending = spending_agg['total'] or 0
            
            # Address: take from user profile or first address
            address = "N/A"
            phone = getattr(u, 'phone', '') or ''
            
            # Address model related_name is 'user_addresses'
            if hasattr(u, 'user_addresses') and u.user_addresses.exists():
                 addr = u.user_addresses.filter(is_default=True).first() or u.user_addresses.first()
                 if addr:
                     address = f"{addr.province}"
                     if addr.phone_number:
                         phone = addr.phone_number

            results.append(AdminUserType(
                id=u.id,
                name=u.get_full_name() or u.username,
                email=u.email,
                phone=phone,
                role=role,
                status=status,
                orders=orders_count,
                spending=float(spending),
                join_date=u.date_joined.strftime("%Y-%m-%d"),
                last_active=u.last_login.strftime("%Y-%m-%d") if u.last_login else "",
                address=address,
                store_name=store_name
            ))
            
        return results

    def resolve_admin_orders(self, info):
        """Resolve list of all orders (SubOrders) with aggregated stats"""
        # Fetch SubOrders to get store-specific orders
        sub_orders = SubOrder.objects.all().select_related('order', 'store', 'order__buyer', 'order__address', 'shipment').order_by('-created_at')
        
        results = []
        for sub in sub_orders:
            # Determine Status from Shipment
            status = 'pending'
            if hasattr(sub, 'shipment'):
                status = sub.shipment.status
            
            # Determine Payment Method from Order -> Payment
            payment_method = 'unknown'
            if hasattr(sub.order, 'payment'):
                payment_method = sub.order.payment.payment_method
            
            # Address
            shipping_address = "N/A"
            if sub.order.address:
                shipping_address = sub.order.address.province
            
            # Products count
            products_count = sub.items.aggregate(count=Sum('quantity'))['count'] or 0
            
            # Format ID
            order_id_str = f"ORD{sub.order.order_id}-S{sub.sub_order_id}"

            results.append(AdminOrderType(
                id=order_id_str,
                customer=sub.order.buyer.get_full_name() or sub.order.buyer.username,
                store=sub.store.name,
                products=products_count,
                total=float(sub.subtotal),
                status=status,
                payment_method=payment_method,
                shipping_address=shipping_address,
                date=sub.created_at.strftime("%Y-%m-%d")
            ))
            
        return results

    def resolve_admin_products(self, info):
        """Resolve list of all products with aggregated stats"""
        from orders.models import OrderItem
        
        products = Product.objects.all().select_related('store', 'category').order_by('-created_at')
        
        results = []
        for p in products:
            # Calculate total stock from variants
            stock = p.variants.aggregate(total=Sum('stock'))['total'] or 0
            
            # Calculate sold count from OrderItems
            sold = OrderItem.objects.filter(variant__product=p).aggregate(total=Sum('quantity'))['total'] or 0
            
            # Get first image
            image_url = ""
            first_image = p.gallery_images.filter(is_thumbnail=True).first() or p.gallery_images.first()
            if first_image and first_image.image:
                image_url = first_image.image.url
            
            # Determine status (using is_active as proxy for approval status)
            # In real scenario, you might have a separate approval_status field
            status = 'approved' if p.is_active else 'rejected'
            
            results.append(AdminProductType(
                id=p.product_id,
                name=p.name,
                store=p.store.name,
                category=p.category.name,
                price=float(p.base_price),
                stock=stock,
                sold=sold,
                rating=float(p.rating),
                reviews=p.review_count,
                status=status,
                image=image_url
            ))
            
        return results

    def resolve_admin_analytics(self, info, range='30d', limit=12):
        """Resolve analytics data with revenue growth calculation"""
        from .types import RevenueTrendType, CategoryPerformanceType, RegionalDistributionType, UserGrowthType, KeyMetricsType
        from orders.models import OrderItem
        from dateutil.relativedelta import relativedelta
        
        # Calculate revenue trend for last N months
        revenue_trend = []
        today = timezone.now().date()
        
        for i in range(limit - 1, -1, -1):
            month_date = today - relativedelta(months=i)
            month_start = month_date.replace(day=1)
            if i == 0:
                month_end = today
            else:
                month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
            
            # Get orders for this month
            month_orders = SubOrder.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end
            )
            
            revenue = month_orders.aggregate(total=Sum('subtotal'))['total'] or 0
            orders_count = month_orders.count()
            
            # Calculate growth (compare with previous month)
            growth = 0.0
            if i > 0:
                prev_month_start = month_start - relativedelta(months=1)
                prev_month_end = month_start - timedelta(days=1)
                prev_revenue = SubOrder.objects.filter(
                    created_at__gte=prev_month_start,
                    created_at__lte=prev_month_end
                ).aggregate(total=Sum('subtotal'))['total'] or 0
                
                if prev_revenue > 0:
                    growth = ((revenue - prev_revenue) / prev_revenue) * 100
            
            revenue_trend.append(RevenueTrendType(
                month=month_date.strftime("%m/%Y"),
                revenue=float(revenue),
                orders=orders_count,
                growth=float(growth)
            ))
        
        # Category performance
        category_performance = []
        categories = Category.objects.annotate(
            total_sales=Sum('products__variants__order_items__price_at_order'),
            total_orders=Count('products__variants__order_items', distinct=True)
        ).order_by('-total_sales')[:5]
        
        for cat in categories:
            category_performance.append(CategoryPerformanceType(
                name=cat.name,
                sales=float(cat.total_sales or 0),
                orders=cat.total_orders or 0
            ))
        
        # Regional distribution (by province from addresses)
        regional_data = []
        total_orders = Order.objects.count()
        
        if total_orders > 0:
            regions = Address.objects.filter(
                address_orders__isnull=False
            ).values('province').annotate(
                count=Count('address_orders')
            ).order_by('-count')[:5]
            
            for reg in regions:
                percent = (reg['count'] / total_orders) if total_orders > 0 else 0
                regional_data.append(RegionalDistributionType(
                    region=reg['province'] or 'Unknown',
                    value=reg['count'],
                    percent=float(percent)
                ))
        
        # User growth (last 12 months)
        user_growth = []
        for i in range(11, -1, -1):
            month_date = today - relativedelta(months=i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
            
            # Count customers (users who made orders)
            customers = User.objects.filter(
                orders__created_at__gte=month_start,
                orders__created_at__lte=month_end
            ).distinct().count()
            
            # Count sellers (users who own stores)
            sellers = StoreUser.objects.filter(
                role='owner',
                created_at__gte=month_start,
                created_at__lte=month_end
            ).count()
            
            user_growth.append(UserGrowthType(
                month=month_date.strftime("%m/%Y"),
                customers=customers,
                sellers=sellers
            ))
        
        # Key metrics
        # Revenue growth (current month vs last month)
        current_month_start = today.replace(day=1)
        current_revenue = SubOrder.objects.filter(
            created_at__gte=current_month_start
        ).aggregate(total=Sum('subtotal'))['total'] or 0
        
        last_month_start = current_month_start - relativedelta(months=1)
        last_month_end = current_month_start - timedelta(days=1)
        last_revenue = SubOrder.objects.filter(
            created_at__gte=last_month_start,
            created_at__lte=last_month_end
        ).aggregate(total=Sum('subtotal'))['total'] or 0
        
        revenue_growth = 0.0
        if last_revenue > 0:
            revenue_growth = ((current_revenue - last_revenue) / last_revenue) * 100
        
        # Average order value
        total_orders_count = Order.objects.count()
        total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        avg_order_value = (total_revenue / total_orders_count) if total_orders_count > 0 else 0
        
        # Retention rate (users who made more than 1 order)
        repeat_customers = User.objects.annotate(
            order_count=Count('orders')
        ).filter(order_count__gt=1).count()
        total_customers = User.objects.filter(orders__isnull=False).distinct().count()
        retention_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        key_metrics = KeyMetricsType(
            revenue_growth=float(revenue_growth),
            average_order_value=str(avg_order_value),
            retention_rate=float(retention_rate)
        )
        
        return AdminAnalyticsType(
            revenue_trend=revenue_trend,
            category_performance=category_performance,
            regional_distribution=regional_data,
            user_growth=user_growth,
            key_metrics=key_metrics
        )

    def resolve_admin_vouchers(self, info):
        """Resolve all vouchers for admin management"""
        from discount.models import OrderVoucher
        
        vouchers = Voucher.objects.all().annotate(
            times_used=Count('order_vouchers')
        ).order_by('-created_at')
        
        return vouchers

    def resolve_admin_voucher_by_id(self, info, voucher_id):
        """Resolve a specific voucher by ID for admin management"""
        try:
            return Voucher.objects.annotate(
                times_used=Count('order_vouchers')
            ).get(voucher_id=voucher_id)
        except Voucher.DoesNotExist:
            return None

class ToggleVoucher(graphene.Mutation):
    class Arguments:
        voucher_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    voucher = graphene.Field('graphql_api.discount.types.VoucherType')
    
    def mutate(self, info, voucher_id):
        try:
            voucher = Voucher.objects.get(voucher_id=voucher_id)
            voucher.is_active = not voucher.is_active
            voucher.save()
            
            return ToggleVoucher(
                success=True,
                message=f"Voucher {'activated' if voucher.is_active else 'deactivated'} successfully",
                voucher=voucher
            )
        except Voucher.DoesNotExist:
            return ToggleVoucher(
                success=False,
                message="Voucher not found",
                voucher=None
            )

class CreateAdminVoucher(graphene.Mutation):
    class Arguments:
        code = graphene.String(required=True)
        name = graphene.String(required=True)
        type = graphene.String(required=True)
        discount_type = graphene.String(required=True)
        discount_value = graphene.Decimal(required=True)
        description = graphene.String()
        min_order_amount = graphene.Decimal(required=True)
        max_discount = graphene.Decimal()
        start_date = graphene.Date(required=True)
        end_date = graphene.Date(required=True)
        usage_limit = graphene.Int()
        per_user_limit = graphene.Int(required=True)
        is_active = graphene.Boolean()
    
    success = graphene.Boolean()
    message = graphene.String()
    voucher = graphene.Field('graphql_api.discount.types.VoucherType')
    
    def mutate(self, info, code, name, type, discount_type, discount_value, min_order_amount, per_user_limit, start_date, end_date, **kwargs):
        try:
            voucher = Voucher.objects.create(
                code=code.upper(),
                name=name,
                type=type,
                discount_type=discount_type,
                discount_value=discount_value,
                description=kwargs.get('description', ''),
                min_order_amount=min_order_amount,
                max_discount=kwargs.get('max_discount'),
                start_date=start_date,
                end_date=end_date,
                usage_limit=kwargs.get('usage_limit'),
                per_user_limit=per_user_limit,
                is_active=kwargs.get('is_active', True)
            )
            
            return CreateAdminVoucher(
                success=True,
                message="Voucher created successfully",
                voucher=voucher
            )
        except Exception as e:
            return CreateAdminVoucher(
                success=False,
                message=str(e),
                voucher=None
            )

class UpdateAdminVoucher(graphene.Mutation):
    class Arguments:
        voucher_id = graphene.ID(required=True)
        code = graphene.String()
        name = graphene.String()
        type = graphene.String()
        discount_type = graphene.String()
        discount_value = graphene.Decimal()
        description = graphene.String()
        min_order_amount = graphene.Decimal()
        max_discount = graphene.Decimal()
        start_date = graphene.Date()
        end_date = graphene.Date()
        usage_limit = graphene.Int()
        per_user_limit = graphene.Int()
        is_active = graphene.Boolean()
    
    success = graphene.Boolean()
    message = graphene.String()
    voucher = graphene.Field('graphql_api.discount.types.VoucherType')
    
    def mutate(self, info, voucher_id, **kwargs):
        try:
            voucher = Voucher.objects.get(voucher_id=voucher_id)
            
            # Update only provided fields
            if 'code' in kwargs and kwargs['code']:
                voucher.code = kwargs['code'].upper()
            if 'name' in kwargs and kwargs['name']:
                voucher.name = kwargs['name']
            if 'type' in kwargs and kwargs['type']:
                voucher.type = kwargs['type']
            if 'discount_type' in kwargs and kwargs['discount_type']:
                voucher.discount_type = kwargs['discount_type']
            if 'discount_value' in kwargs and kwargs['discount_value'] is not None:
                voucher.discount_value = kwargs['discount_value']
            if 'description' in kwargs:
                voucher.description = kwargs['description']
            if 'min_order_amount' in kwargs and kwargs['min_order_amount'] is not None:
                voucher.min_order_amount = kwargs['min_order_amount']
            if 'max_discount' in kwargs:
                voucher.max_discount = kwargs['max_discount']
            if 'start_date' in kwargs and kwargs['start_date']:
                voucher.start_date = kwargs['start_date']
            if 'end_date' in kwargs and kwargs['end_date']:
                voucher.end_date = kwargs['end_date']
            if 'usage_limit' in kwargs:
                voucher.usage_limit = kwargs['usage_limit']
            if 'per_user_limit' in kwargs and kwargs['per_user_limit'] is not None:
                voucher.per_user_limit = kwargs['per_user_limit']
            if 'is_active' in kwargs and kwargs['is_active'] is not None:
                voucher.is_active = kwargs['is_active']
            
            voucher.save()
            
            return UpdateAdminVoucher(
                success=True,
                message="Voucher updated successfully",
                voucher=voucher
            )
        except Voucher.DoesNotExist:
            return UpdateAdminVoucher(
                success=False,
                message="Voucher not found",
                voucher=None
            )
        except Exception as e:
            return UpdateAdminVoucher(
                success=False,
                message=str(e),
                voucher=None
            )

class DeleteVoucherMutation(graphene.Mutation):
    class Arguments:
        voucher_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, voucher_id):
        try:
            voucher = Voucher.objects.get(voucher_id=voucher_id)
            voucher.delete()
            
            return DeleteVoucherMutation(
                success=True,
                message="Voucher deleted successfully"
            )
        except Voucher.DoesNotExist:
            return DeleteVoucherMutation(
                success=False,
                message="Voucher not found"
            )

class LockStore(graphene.Mutation):
    class Arguments:
        store_id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    store = graphene.Field(AdminStoreType)

    def mutate(self, info, store_id):
        try:
            store = Store.objects.get(store_id=store_id)
            # No permission check as requested
            store.is_active = False
            store.status = 'suspended'
            store.save()
            
            # Return store info (mapped to AdminStoreType just for ID/Status update if needed)
            # Minimal mapping for response
            admin_store = AdminStoreType(
                id=store.store_id,
                name=store.name,
                status='suspended'
            )
            
            return LockStore(success=True, message="Store locked successfully", store=admin_store)
        except Store.DoesNotExist:
            return LockStore(success=False, message="Store not found")
        except Exception as e:
            return LockStore(success=False, message=str(e))

class BanUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(AdminUserType)

    def mutate(self, info, user_id):
        try:
            user = User.objects.get(pk=user_id)
            # Toggle active status (or set to False as "Ban")
            # Usually ban means is_active=False
            user.is_active = False 
            user.save()
            
            return BanUser(success=True, message="User banned successfully")
        except User.DoesNotExist:
            return BanUser(success=False, message="User not found")
        except Exception as e:
            return BanUser(success=False, message=str(e))


class DashboardMutation(graphene.ObjectType):
    lock_store = LockStore.Field()
    ban_user = BanUser.Field()
    toggle_voucher = ToggleVoucher.Field()
    delete_voucher = DeleteVoucherMutation.Field()
    create_admin_voucher = CreateAdminVoucher.Field()
    update_admin_voucher = UpdateAdminVoucher.Field()
