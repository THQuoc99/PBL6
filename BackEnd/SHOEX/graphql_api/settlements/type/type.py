import graphene
from graphene_django import DjangoObjectType

from settlements.models import Settlement, SettlementItem


class SettlementItemType(DjangoObjectType):
    class Meta:
        model = SettlementItem
        fields = "__all__"


class SettlementType(DjangoObjectType):
    class Meta:
        model = Settlement
        fields = "__all__"
