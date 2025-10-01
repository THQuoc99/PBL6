"""
SHOEX GraphQL Schema - Phiên bản đơn giản để test
"""
import graphene

class ProductType(graphene.ObjectType):
    """Type đơn giản cho Product"""
    id = graphene.ID()
    name = graphene.String()
    price = graphene.Float()
    description = graphene.String()

class Query(graphene.ObjectType):
    """Root Query cho SHOEX"""
    
    # Health check
    health = graphene.String()
    
    # Simple product queries
    products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.ID())
    
    def resolve_health(self, info):
        return "SHOEX GraphQL API is running!"
    
    def resolve_products(self, info):
        # Mock data cho test
        return [
            {"id": "1", "name": "Nike Air Max", "price": 2500000, "description": "Giày thể thao cao cấp"},
            {"id": "2", "name": "Adidas Ultra Boost", "price": 3000000, "description": "Giày chạy bộ chuyên nghiệp"},
            {"id": "3", "name": "Converse All Star", "price": 1200000, "description": "Giày thời trang classic"},
        ]
    
    def resolve_product(self, info, id):
        # Mock data cho test
        products = {
            "1": {"id": "1", "name": "Nike Air Max", "price": 2500000, "description": "Giày thể thao cao cấp"},
            "2": {"id": "2", "name": "Adidas Ultra Boost", "price": 3000000, "description": "Giày chạy bộ chuyên nghiệp"},
            "3": {"id": "3", "name": "Converse All Star", "price": 1200000, "description": "Giày thời trang classic"},
        }
        return products.get(id)

class ProductCreateInput(graphene.InputObjectType):
    """Input để tạo sản phẩm"""
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    description = graphene.String()

class ProductCreate(graphene.Mutation):
    """Mutation tạo sản phẩm"""
    
    class Arguments:
        input = ProductCreateInput(required=True)
    
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        # Mock mutation
        new_product = {
            "id": "new_id",
            "name": input.name,
            "price": input.price,
            "description": input.get('description', '')
        }
        
        return ProductCreate(
            product=new_product,
            success=True,
            errors=[]
        )

class Mutation(graphene.ObjectType):
    """Root Mutation cho SHOEX"""
    product_create = ProductCreate.Field()

# Tạo schema
schema = graphene.Schema(query=Query, mutation=Mutation)