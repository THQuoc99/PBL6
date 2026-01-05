# orders/graphql/mutations.py
import graphene
from django.db import transaction
from decimal import Decimal
from django.utils import timezone

from orders.models import Order, SubOrder, OrderItem
from payments.models import Payment
from shipments.models import Shipment
from address.models import Address
from products.models import ProductVariant
from store.models import Store, StoreUser

from ..Type.inputType import CreateOrderInput, SubOrderInput, OrderItemInput
from ..ultis.create_ghtk_order import create_ghtk_orders, create_ghtk_order_for_suborder
from ..ultis.CancelSubOrder import cancel_ghtk_order


class ConfirmSubOrderShipment(graphene.Mutation):
    class Arguments:
        subOrderId = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    result = graphene.JSONString()

    @classmethod
    def mutate(cls, root, info, subOrderId):
        user = info.context.user
        if not user or not user.is_authenticated:
            return cls(success=False, message="Unauthenticated", result=None)

        try:
            with transaction.atomic():
                sub = SubOrder.objects.select_related('store', 'shipment', 'order').get(pk=int(subOrderId))
                shipment = getattr(sub, 'shipment', None)
                if not shipment:
                    return cls(success=False, message='Shipment for suborder not found', result=None)

                # Permission: allow staff or active StoreUser membership for this store
                allowed = False
                if getattr(user, 'is_staff', False):
                    allowed = True
                else:
                    allowed = StoreUser.objects.filter(store=sub.store, user=user, status='active').exists()

                if not allowed:
                    return cls(success=False, message='Permission denied', result=None)

                # Only allow confirming when shipment is pending
                if shipment.status != 'pending':
                    return cls(success=False, message='Shipment is not pending', result=None)

                # Call helper to create GHTK order for this suborder (this will update shipment.status -> 'shipping')
                res = create_ghtk_order_for_suborder(sub.sub_order_id)

            return cls(success=True, message='Shipment confirmed and GHTK order created', result=res)
        except SubOrder.DoesNotExist:
            return cls(success=False, message='SubOrder not found', result=None)
        except Exception as e:
            return cls(success=False, message=str(e), result=None)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order_id = graphene.ID()
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        user = info.context.user
        if not user or not user.is_authenticated:
            return cls(success=False, message="Unauthenticated")

        with transaction.atomic():

            # 1. Address
            try:
                # Address model uses `address_id` (not `id`) as the field name in DB
                # Query by the actual field name to avoid "Cannot resolve keyword 'id'" error.
                address = Address.objects.get(address_id=input.address_id, user=user)
            except Address.DoesNotExist:
                return cls(success=False, message="Invalid address")

            # 2. Create Order
            order = Order.objects.create(
                buyer=user,
                total_amount=input.total_amount,
                shipping_fee=input.shipping_fee,
                address=address,
            )

            # 3. Create SubOrders + Items
            for sub in input.sub_orders:
                # Store model uses `store_id` field name; avoid lookup by non-existent `id` field
                store = Store.objects.get(store_id=sub.store_id)

                sub_order = SubOrder.objects.create(
                    order=order,
                    store=store,
                    shipping_fee=sub.shipping_fee,
                    subtotal=sub.subtotal,
                )

                total_weight = Decimal('0.0')

                for item in sub.items:
                    variant = ProductVariant.objects.select_for_update().get(
                        variant_id=item.variant_id
                    )

                    if variant.stock < item.quantity:
                        raise Exception(f"Out of stock: {variant.sku}")

                    OrderItem.objects.create(
                        order=order,
                        sub_order=sub_order,
                        variant=variant,
                        quantity=item.quantity,
                        price_at_order=item.price_at_order,
                    )

                    # 1. Cộng khối lượng
                    total_weight += variant.weight * item.quantity

                    # Trừ kho
                    variant.stock -= item.quantity
                    variant.save(update_fields=['stock'])

                # 4. Shipment cho từng store (pending_confirmation)
                Shipment.objects.create(
                    user=user,
                    sub_order=sub_order,
                    store=store,
                    pick_money=sub_order.shipping_fee + sub_order.subtotal,
                    value=sub_order.subtotal,
                    transport='road ',
                    status='pending',  # nội bộ người bán xử lý
                    total_weight=total_weight,
                    
                )

            # 5. Payment (1 payment / order)
            Payment.objects.create(
                order=order,
                user=user,
                payment_method=input.payment_method,
                amount=input.total_amount,
                status='pending',
            )

        return cls(
            success=True,
            message="Order created successfully",
            order_id=order.order_id,
        )


class CreateGHTKOrders(graphene.Mutation):
    class Arguments:
        orderId = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    results = graphene.JSONString()

    @classmethod
    def mutate(cls, root, info, orderId):
        user = info.context.user
        if not user or not user.is_authenticated:
            return cls(success=False, message="Unauthenticated", results=None)

        try:
            # call util to create GHTK orders for the given order id
            results = create_ghtk_orders(order_id=int(orderId))
            return cls(success=True, message="GHTK orders created", results=results)
        except Exception as e:
            return cls(success=False, message=str(e), results=None)


class CancelOrder(graphene.Mutation):
    class Arguments:
        orderId = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, orderId):
        user = info.context.user
        if not user or not user.is_authenticated:
            return cls(success=False, message="Unauthenticated")

        try:
            with transaction.atomic():
                order = Order.objects.select_related('payment').prefetch_related('sub_orders__shipment').get(pk=int(orderId))

                # Cancel payment if exists
                payment = getattr(order, 'payment', None)
                if payment:
                    payment.status = 'cancelled'
                    payment.save(update_fields=['status', 'updated_at'] if hasattr(payment, 'updated_at') else ['status'])

                # Cancel all shipments for suborders. If a shipment has external tracking_code (GHTK),
                # attempt to cancel via carrier API first; on failure fallback to local cancel.
                for sub in order.sub_orders.all():
                    shipment = getattr(sub, 'shipment', None)
                    if not shipment:
                        continue
                    if shipment.tracking_code:
                        try:
                            cancel_ghtk_order(shipment_id=shipment.shipment_id, reason='Cancelled by order cancellation')
                            # cancel_ghtk_order updates shipment.status and creates tracking log
                            continue
                        except Exception as e:
                            # fallback to local cancellation but log the error
                            print(f"Cancel GHTK failed for shipment {shipment.shipment_id}: {e}")
                    shipment.status = 'cancelled'
                    shipment.updated_at = timezone.now()
                    shipment.save(update_fields=['status', 'updated_at'])

            return cls(success=True, message='Order cancelled')
        except Order.DoesNotExist:
            return cls(success=False, message='Order not found')
        except Exception as e:
            return cls(success=False, message=str(e))


class CancelSubOrder(graphene.Mutation):
    class Arguments:
        subOrderId = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, subOrderId):
        user = info.context.user
        if not user or not user.is_authenticated:
            return cls(success=False, message="Unauthenticated")

        try:
            with transaction.atomic():
                sub = SubOrder.objects.select_related('order').prefetch_related('order__sub_orders__shipment').get(pk=int(subOrderId))
                shipment = getattr(sub, 'shipment', None)
                if not shipment:
                    return cls(success=False, message='Shipment for suborder not found')

                # If shipment is linked to external carrier (tracking_code), try cancel via carrier API
                if shipment.tracking_code:
                    try:
                        cancel_ghtk_order(shipment_id=shipment.shipment_id, reason='Cancelled by suborder cancellation')
                    except Exception as e:
                        print(f"Cancel GHTK failed for shipment {shipment.shipment_id}: {e}")
                        # fallback to local cancellation
                        shipment.status = 'cancelled'
                        shipment.updated_at = timezone.now()
                        shipment.save(update_fields=['status', 'updated_at'])
                else:
                    shipment.status = 'cancelled'
                    shipment.updated_at = timezone.now()
                    shipment.save(update_fields=['status', 'updated_at'])

                # If all suborders shipments of parent order are cancelled, mark payment cancelled too
                parent = sub.order
                all_cancelled = True
                for s in parent.sub_orders.all():
                    sh = getattr(s, 'shipment', None)
                    if sh and sh.status != 'cancelled':
                        all_cancelled = False
                        break

                payment = getattr(parent, 'payment', None)
                if payment and all_cancelled:
                    payment.status = 'cancelled'
                    payment.save(update_fields=['status', 'updated_at'] if hasattr(payment, 'updated_at') else ['status'])

            return cls(success=True, message='SubOrder cancelled')
        except SubOrder.DoesNotExist:
            return cls(success=False, message='SubOrder not found')
        except Exception as e:
            return cls(success=False, message=str(e))

