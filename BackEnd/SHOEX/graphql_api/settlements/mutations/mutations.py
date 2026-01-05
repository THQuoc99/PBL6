from graphql_api.order.ultis.updateStatusOrder import update_status_for_suborder
import graphene
from decimal import Decimal

from django.db import transaction

from settlements.models import Settlement, SettlementItem
from store.models import Store
from orders.models import SubOrder


class CreateSettlement(graphene.Mutation):
    class Arguments:
        store_id = graphene.ID(required=True)

    settlement_id = graphene.ID()
    total_amount = graphene.Decimal()
    status = graphene.String()

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, store_id):
        # 1. Lấy store
        try:
            store = Store.objects.get(pk=store_id)
        except Store.DoesNotExist:
            raise Exception("Store không tồn tại")

        # 2. Lấy SubOrder đủ điều kiện rút tiền
        sub_orders = (
            SubOrder.objects
            .select_related("shipment")
            .filter(
                store=store,
                shipment__status="completed",
                # settlement_item__isnull=True,
            )
        )
        for s in sub_orders:
                try:
                    update_status_for_suborder(s.sub_order_id)
                except Exception:
                    # ignore errors to avoid blocking the API response
                    pass

        if not sub_orders.exists():
            raise Exception("Không có đơn hàng nào đủ điều kiện rút tiền")

        # 3. Tính tổng tiền
        total_amount = Decimal("0.00")
        items_data = []

        for sub_order in sub_orders:
            # subtotal + shipping_fee
            amount = (sub_order.subtotal or Decimal("0.00")) + (sub_order.shipping_fee or Decimal("0.00"))
            total_amount += amount

            items_data.append({
                "sub_order": sub_order,
                "amount": amount,
            })

        # 4. Tạo Settlement
        settlement = Settlement.objects.create(
            store=store,
            total_amount=total_amount,
            status="pending",
        )

        # 5. Tạo SettlementItem
        SettlementItem.objects.bulk_create([
            SettlementItem(
                settlement=settlement,
                sub_order=item["sub_order"],
                amount=item["amount"],
            )
            for item in items_data
        ])

        return CreateSettlement(
            settlement_id=settlement.settlement_id,
            total_amount=settlement.total_amount,
            status=settlement.status,
        )


class SettlementMutations(graphene.ObjectType):
    create_settlement = CreateSettlement.Field()
