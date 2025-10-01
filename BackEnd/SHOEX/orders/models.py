from django.db import models

class Province(models.Model):
    province_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã tỉnh/thành",
        help_text="ID tự tăng, duy nhất cho mỗi tỉnh/thành"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Tên tỉnh/thành",
        help_text="Tên tỉnh/thành (VD: Hà Nội)"
    )

    def __str__(self):
        return self.name


class District(models.Model):
    district_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã huyện",
        help_text="ID tự tăng, duy nhất cho mỗi huyện"
    )
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name='districts',
        verbose_name="Tỉnh/thành",
        help_text="Tỉnh/thành chứa huyện"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Tên huyện",
        help_text="Tên huyện (VD: Quận Hoàn Kiếm)"
    )

    def __str__(self):
        return self.name


class Ward(models.Model):
    ward_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã xã",
        help_text="ID tự tăng, duy nhất cho mỗi xã"
    )
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='wards',
        verbose_name="Huyện",
        help_text="Huyện chứa xã"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Tên xã",
        help_text="Tên xã (VD: Phường Hàng Trống)"
    )

    def __str__(self):
        return self.name


class Hamlet(models.Model):
    hamlet_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã thôn/xóm",
        help_text="ID tự tăng, duy nhất cho mỗi thôn/xóm"
    )
    ward = models.ForeignKey(
        Ward,
        on_delete=models.CASCADE,
        related_name='hamlets',
        verbose_name="Xã",
        help_text="Xã chứa thôn/xóm"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Tên thôn/xóm",
        help_text="Tên thôn/xóm"
    )

    def __str__(self):
        return self.name


class Address(models.Model):
    address_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã địa chỉ",
        help_text="ID tự tăng, duy nhất cho mỗi địa chỉ"
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name="Người dùng",
        help_text="Người dùng sở hữu địa chỉ này"
    )
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name="Tỉnh/thành",
        help_text="Tỉnh/thành của địa chỉ"
    )
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name="Huyện",
        help_text="Huyện của địa chỉ"
    )
    ward = models.ForeignKey(
        Ward,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name="Xã",
        help_text="Xã của địa chỉ"
    )
    hamlet = models.ForeignKey(
        Hamlet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='addresses',
        verbose_name="Thôn/xóm",
        help_text="Thôn/xóm của địa chỉ (có thể để trống)"
    )
    detail = models.CharField(
        max_length=255,
        verbose_name="Địa chỉ chi tiết",
        help_text="Địa chỉ chi tiết (VD: số nhà, ngõ, đường)"
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Địa chỉ mặc định",
        help_text="Đánh dấu nếu đây là địa chỉ mặc định"
    )

    def __str__(self):
        return f"{self.detail}, {self.ward}, {self.district}, {self.province}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã đơn hàng",
        help_text="ID tự tăng, duy nhất cho mỗi đơn hàng"
    )
    buyer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Người mua",
        help_text="Người mua thực hiện đơn hàng"
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Địa chỉ giao hàng",
        help_text="Địa chỉ giao hàng của đơn hàng"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Tổng tiền",
        help_text="Tổng số tiền của đơn hàng"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái đơn hàng",
        help_text="Trạng thái hiện tại của đơn hàng"
    )
    shipment_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái vận chuyển",
        help_text="Trạng thái vận chuyển của đơn hàng"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo",
        help_text="Ngày giờ đơn hàng được tạo"
    )

    def __str__(self):
        return f"Order {self.order_id}"


class SubOrder(models.Model):
    sub_order_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã đơn hàng con",
        help_text="ID tự tăng, duy nhất cho mỗi đơn hàng con"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='sub_orders',
        verbose_name="Đơn hàng chính",
        help_text="Đơn hàng chính mà đơn hàng con thuộc về"
    )
    seller = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='sub_orders',
        verbose_name="Người bán",
        help_text="Người bán thực hiện đơn hàng con"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Tổng tiền",
        help_text="Tổng số tiền của đơn hàng con"
    )
    status = models.CharField(
        max_length=10,
        choices=Order.STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái đơn hàng con",
        help_text="Trạng thái hiện tại của đơn hàng con"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo",
        help_text="Ngày giờ đơn hàng con được tạo"
    )

    def __str__(self):
        return f"SubOrder {self.sub_order_id}"


class OrderItem(models.Model):
    order_item_id = models.AutoField(
        primary_key=True,
        verbose_name="Mã mục đơn hàng",
        help_text="ID tự tăng, duy nhất cho mỗi mục đơn hàng"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Đơn hàng",
        help_text="Đơn hàng mà mục này thuộc về"
    )
    sub_order = models.ForeignKey(
        SubOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Đơn hàng con",
        help_text="Đơn hàng con mà mục này thuộc về"
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="Biến thể sản phẩm",
        help_text="Biến thể sản phẩm được đặt hàng"
    )
    quantity = models.IntegerField(
        default=1,
        verbose_name="Số lượng",
        help_text="Số lượng sản phẩm trong mục đơn hàng"
    )
    price_at_order = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Giá tại thời điểm đặt hàng",
        help_text="Giá của sản phẩm tại thời điểm đặt hàng"
    )

    def __str__(self):
        return f"OrderItem {self.order_item_id}"
