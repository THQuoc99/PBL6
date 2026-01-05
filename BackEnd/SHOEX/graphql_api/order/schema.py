import graphene
from graphene import relay
from django.db.models import Q
from orders.models import Order, SubOrder
from .Type.types import OrderType, SubOrderType
from .ultis.updateStatusOrder import update_status_for_order, update_status_for_suborder

class OrderMutations(graphene.ObjectType):
    """Mutations cho Cart"""
    
    from .mutations.mutations import (
        CreateOrder
    )
    from .mutations.mutations import CreateGHTKOrders
    from .mutations.mutations import CancelOrder, CancelSubOrder
    from .mutations.mutations import ConfirmSubOrderShipment

    create_order = CreateOrder.Field()
    create_ghtk_orders = CreateGHTKOrders.Field()
    cancel_order = CancelOrder.Field()
    cancel_sub_order = CancelSubOrder.Field()
    confirm_suborder_shipment = ConfirmSubOrderShipment.Field()


class OrderQueries(graphene.ObjectType):
    """Order-related queries"""

    my_orders = graphene.List(OrderType, description="Danh sách đơn hàng của user đăng nhập")
    orders_by_user = graphene.List(OrderType, user_id=graphene.ID(required=True), description="Danh sách đơn hàng theo user id (test)")

    def resolve_my_orders(self, info, **kwargs):
        user = getattr(info.context, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            return []
        # Lấy danh sách đơn hàng của user
        orders = Order.objects.filter(buyer=user).order_by('-created_at').prefetch_related('sub_orders__shipment')
        print(f"Found {orders.count()} orders for user {user.username} ({user.id})")
        # Cập nhật trạng thái cho các đơn có shipment chưa ở trạng thái cuối
        for order in orders:
            try:
                for sub in order.sub_orders.all():
                    shipment = getattr(sub, 'shipment', None)
                    if shipment and shipment.status in ('pending', 'shipping', 'out_for_delivery'):
                        try:
                            update_status_for_order(order.order_id)
                        except Exception:
                            # không block nếu update lỗi
                            pass
                        break
            except Exception:
                # an toàn: nếu có lỗi khi duyệt sub_orders thì tiếp tục
                pass

        return orders

    def resolve_orders_by_user(self, info, user_id, **kwargs):
        try:
            return Order.objects.filter(buyer__pk=user_id).order_by('-created_at')
        except Exception:
            return []

    sub_orders_by_store = graphene.List(
        SubOrderType,
        store_id=graphene.ID(required=True),
        is_payment=graphene.Boolean(required=False),
        description="Danh sách đơn hàng con (SubOrder) theo store id",
    )

    def resolve_sub_orders_by_store(self, info, store_id, is_payment=None, **kwargs):
        """Trả về danh sách SubOrder theo store.

        Nếu is_payment = True -> chỉ lấy các suborder chưa thuộc SettlementItem
        (tức là chưa có quan hệ settlement_item).
        """
        try:
            qs = (
                SubOrder.objects.filter(store__store_id=store_id)
                .order_by('-created_at')
                .select_related('order', 'store')
                .prefetch_related('items__variant__product')
            )

            # Nếu gọi cho màn Payment (rút tiền) thì chỉ lấy suborder chưa nằm trong SettlementItem
            if is_payment:
                qs = qs.filter(settlement_item__isnull=True)

            # Update each suborder's shipment status (non-blocking)
            for s in qs:
                try:
                    update_status_for_suborder(s.sub_order_id)
                except Exception:
                    # ignore errors to avoid blocking the API response
                    pass

            return qs
        except Exception:
            return []