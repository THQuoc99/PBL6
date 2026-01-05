import graphene

from .type.type import SettlementType, SettlementItemType
from .mutations.mutations import SettlementMutations


class SettlementQuery(graphene.ObjectType):
    # simple placeholder, can be expanded later
    settlements = graphene.List(SettlementType, store_id=graphene.ID(required=False))

    def resolve_settlements(self, info, store_id=None):
        from settlements.models import Settlement

        qs = Settlement.objects.all()
        if store_id is not None:
            qs = qs.filter(store_id=store_id)
        return qs


class SettlementMutation(SettlementMutations, graphene.ObjectType):
    pass
