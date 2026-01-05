from graphene_django import DjangoObjectType
import graphene
from address.models import Address


class AddressType(DjangoObjectType):
    """GraphQL type cho Address model"""
    
    full_address = graphene.String()
    
    class Meta:
        model = Address
        fields = "__all__"

    def resolve_full_address(self, info):
        """Trả về địa chỉ đầy đủ"""
        return self.full_address