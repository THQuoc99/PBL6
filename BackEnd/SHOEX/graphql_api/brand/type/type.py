from graphene_django import DjangoObjectType
from django.db.models import Q, Max
from django.utils import timezone
from decimal import Decimal
from brand.models import Brand
class BrandType(DjangoObjectType):
    class Meta:
        model = Brand
        fields = "__all__"
