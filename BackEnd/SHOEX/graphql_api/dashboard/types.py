import graphene

class RevenueData(graphene.ObjectType):
    day = graphene.String()
    revenue = graphene.Float()
    orders = graphene.Int()

class TopStore(graphene.ObjectType):
    name = graphene.String()
    revenue = graphene.Float()
    orders = graphene.Int()
    rating = graphene.Float()

class CategoryData(graphene.ObjectType):
    name = graphene.String()
    value = graphene.Int()
    color = graphene.String()

class RecentActivity(graphene.ObjectType):
    id = graphene.Int()
    type = graphene.String()
    text = graphene.String()
    time = graphene.String()
    status = graphene.String()

class DashboardStats(graphene.ObjectType):
    total_revenue = graphene.Float()
    total_orders = graphene.Int()
    total_stores = graphene.Int()
    total_users = graphene.Int()
    
    # Complex data
    revenue_by_day = graphene.List(RevenueData)
    top_stores = graphene.List(TopStore)
    product_by_category = graphene.List(CategoryData)
    recent_activities = graphene.List(RecentActivity)

class AdminStoreType(graphene.ObjectType):
    id = graphene.ID() # store_id
    name = graphene.String()
    owner_name = graphene.String()
    email = graphene.String()
    phone = graphene.String()
    address = graphene.String()
    status = graphene.String()
    revenue = graphene.Float()
    orders = graphene.Int()
    products = graphene.Int()
    rating = graphene.Float()
    join_date = graphene.String()
    avatar = graphene.String()

class AdminUserType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    email = graphene.String()
    phone = graphene.String()
    role = graphene.String()
    status = graphene.String()
    orders = graphene.Int()
    spending = graphene.Float()
    join_date = graphene.String()
    last_active = graphene.String()
    address = graphene.String()
    store_name = graphene.String()

class AdminOrderType(graphene.ObjectType):
    id = graphene.ID()
    customer = graphene.String()
    store = graphene.String()
    products = graphene.Int()
    total = graphene.Float()
    status = graphene.String()
    payment_method = graphene.String()
    shipping_address = graphene.String()
    date = graphene.String()

class AdminProductType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    store = graphene.String()
    category = graphene.String()
    price = graphene.Float()
    stock = graphene.Int()
    sold = graphene.Int()
    rating = graphene.Float()
    reviews = graphene.Int()
    status = graphene.String()
    image = graphene.String()

class RevenueTrendType(graphene.ObjectType):
    month = graphene.String()
    revenue = graphene.Float()
    orders = graphene.Int()
    growth = graphene.Float()

class CategoryPerformanceType(graphene.ObjectType):
    name = graphene.String()
    sales = graphene.Float()
    orders = graphene.Int()

class RegionalDistributionType(graphene.ObjectType):
    region = graphene.String()
    value = graphene.Int()
    percent = graphene.Float()

class UserGrowthType(graphene.ObjectType):
    month = graphene.String()
    customers = graphene.Int()
    sellers = graphene.Int()

class KeyMetricsType(graphene.ObjectType):
    revenue_growth = graphene.Float()
    average_order_value = graphene.String()
    retention_rate = graphene.Float()

class AdminAnalyticsType(graphene.ObjectType):
    revenue_trend = graphene.List(RevenueTrendType)
    category_performance = graphene.List(CategoryPerformanceType)
    regional_distribution = graphene.List(RegionalDistributionType)
    user_growth = graphene.List(UserGrowthType)
    key_metrics = graphene.Field(KeyMetricsType)
