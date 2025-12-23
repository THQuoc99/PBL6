"""
Helper functions to create notifications for various events
"""
from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()


def create_notification(user, title, message, notification_type, **kwargs):
    """
    Create a notification for a user
    
    Args:
        user: User object or user ID
        title: Notification title
        message: Notification message
        notification_type: Type of notification (order, promotion, system, shop_follow, platform)
        **kwargs: Additional fields (order_id, shop_id, shop_name)
    """
    if isinstance(user, int):
        user = User.objects.get(id=user)
    
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=notification_type,
        order_id=kwargs.get('order_id'),
        shop_id=kwargs.get('shop_id'),
        shop_name=kwargs.get('shop_name'),
    )
    return notification


def notify_order_created(user, order_id):
    """Notify user when order is created"""
    return create_notification(
        user=user,
        title="Đơn hàng đã được tạo",
        message=f"Đơn hàng #{order_id} của bạn đã được tạo thành công. Chúng tôi đang xử lý đơn hàng.",
        notification_type='order',
        order_id=order_id
    )


def notify_order_status_update(user, order_id, status):
    """Notify user when order status changes"""
    status_messages = {
        'confirmed': 'Đơn hàng đã được xác nhận',
        'processing': 'Đơn hàng đang được xử lý',
        'shipping': 'Đơn hàng đang được giao',
        'delivered': 'Đơn hàng đã được giao thành công',
        'cancelled': 'Đơn hàng đã bị hủy',
    }
    
    return create_notification(
        user=user,
        title=status_messages.get(status, 'Cập nhật đơn hàng'),
        message=f"Đơn hàng #{order_id} - {status_messages.get(status, status)}",
        notification_type='order',
        order_id=order_id
    )


def notify_shop_new_product(followers, shop_id, shop_name, product_name):
    """Notify shop followers about new product"""
    notifications = []
    for user in followers:
        notif = create_notification(
            user=user,
            title=f"{shop_name} vừa ra mắt sản phẩm mới",
            message=f"Khám phá ngay {product_name} từ {shop_name}!",
            notification_type='shop_follow',
            shop_id=shop_id,
            shop_name=shop_name
        )
        notifications.append(notif)
    return notifications


def notify_shop_promotion(followers, shop_id, shop_name, promotion_title, discount):
    """Notify shop followers about promotion"""
    notifications = []
    for user in followers:
        notif = create_notification(
            user=user,
            title=f"🔥 {shop_name} đang giảm giá {discount}%",
            message=f"{promotion_title} - Mua ngay kẻo lỡ!",
            notification_type='shop_follow',
            shop_id=shop_id,
            shop_name=shop_name
        )
        notifications.append(notif)
    return notifications


def notify_platform_flash_sale(users, sale_title, discount):
    """Notify users about platform flash sale"""
    notifications = []
    for user in users:
        notif = create_notification(
            user=user,
            title=f"⚡ Flash Sale - Giảm đến {discount}%",
            message=f"{sale_title} - Nhanh tay săn deal!",
            notification_type='platform'
        )
        notifications.append(notif)
    return notifications


def notify_platform_voucher(users, voucher_code, discount):
    """Notify users about new voucher"""
    notifications = []
    for user in users:
        notif = create_notification(
            user=user,
            title=f"🎁 Mã giảm giá {discount}% dành cho bạn",
            message=f"Sử dụng mã {voucher_code} để nhận ưu đãi. Có hiệu lực trong 7 ngày!",
            notification_type='platform'
        )
        notifications.append(notif)
    return notifications


def notify_platform_announcement(users, title, message):
    """General platform announcement"""
    notifications = []
    for user in users:
        notif = create_notification(
            user=user,
            title=title,
            message=message,
            notification_type='platform'
        )
        notifications.append(notif)
    return notifications


def notify_promotion_expiring(user, promotion_name, hours_left):
    """Notify user about expiring promotion"""
    return create_notification(
        user=user,
        title=f"⏰ Khuyến mãi sắp hết hạn",
        message=f"{promotion_name} chỉ còn {hours_left} giờ nữa. Mua ngay!",
        notification_type='promotion'
    )
