import graphene
from ..ultis.createVNPayURL import create_payment_url


class CreateVnPayLink(graphene.Mutation):
    class Arguments:
        order_id = graphene.ID(required=True)
        amount = graphene.Float(required=True)  # ✅ FLOAT
        isStore = graphene.Boolean(required=False)

    url = graphene.String()

    def mutate(self, info, order_id, amount, isStore=None):
        # Convert float → int VND
        amount_vnd = int(round(amount))
        url = create_payment_url(
            order_id=str(order_id),
            amount=amount_vnd,
            ip_addr="127.0.0.1",
            isStore=isStore
        )
        return CreateVnPayLink(url=url)
