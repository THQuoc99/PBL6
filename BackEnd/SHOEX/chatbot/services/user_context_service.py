from cart.models import Cart
from orders.models import Order, OrderItem


def get_user_context(user, message):
    """Get user-specific context (cart, orders) for personalized responses."""
    if not user or not user.is_authenticated:
        return ""
    
    msg = message.lower()
    
    # Cart information - khi user hỏi về giỏ hàng
    if "giỏ" in msg:
        try:
            cart = Cart.objects.filter(user=user).first()
            if cart:
                items = cart.items.select_related('variant', 'variant__product').all()
                if items:
                    details = []
                    for item in items:
                        combo_info = item.variant.option_combinations
                        if isinstance(combo_info, dict):
                            variant_str = ", ".join([f"{k}: {v}" for k, v in combo_info.items()])
                        else:
                            variant_str = str(combo_info)
                        details.append(f"- {item.variant.product.name} ({variant_str}) x{item.quantity}: {item.subtotal:,.0f}đ")
                    
                    context = f"Giỏ hàng ({cart.total_items} sản phẩm):\n" + "\n".join(details)
                    context += f"\nTổng cộng: {cart.total_amount:,.0f}đ"
                    return context
                else:
                    return "Giỏ hàng của bạn đang trống."
            else:
                return "Giỏ hàng của bạn đang trống."
        except Exception as e:
            return f"Không thể lấy thông tin giỏ hàng: {str(e)}"
    
    # Order history - khi user hỏi về đơn hàng
    if "đơn" in msg:
        try:
            orders = Order.objects.filter(buyer=user).order_by('-created_at')[:5]
            if orders:
                details = []
                for order in orders:
                    status_display = dict(Order.STATUS_CHOICES).get(order.status, order.status)
                    details.append(f"- Đơn #{order.order_id} ({status_display}): {order.total_amount:,.0f}đ")
                return "Đơn hàng gần đây:\n" + "\n".join(details)
            else:
                return "Bạn chưa có đơn hàng nào."
        except Exception as e:
            return f"Không thể lấy thông tin đơn hàng: {str(e)}"
    
    # General context - khi không hỏi cụ thể
    context_parts = []
    try:
        orders = Order.objects.filter(buyer=user).order_by('-created_at')[:3]
        if orders.count() > 0:
            context_parts.append(f"Đã có {orders.count()} đơn hàng gần đây")
        
        cart = Cart.objects.filter(user=user).first()
        if cart and cart.total_items > 0:
            context_parts.append(f"Giỏ hàng: {cart.total_items} sản phẩm")
    except Exception:
        pass
    
    if context_parts:
        return "Thông tin khách hàng:\n" + "\n".join(context_parts)
    return ""
