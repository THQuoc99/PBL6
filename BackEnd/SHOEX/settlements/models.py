from django.db import models

# Create your models here.
class Settlement(models.Model):
    settlement_id = models.AutoField(primary_key=True)

    store = models.ForeignKey(
        'store.Store',
        on_delete=models.CASCADE,
        related_name='settlements'
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Chờ thanh toán'),
            ('paid', 'Đã thanh toán'),
            ('cancelled', 'Huỷ'),
        ],
        default='pending'
    )

    note = models.TextField(
        blank=True,
        null=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

class SettlementItem(models.Model):
    settlement_item_id = models.AutoField(primary_key=True)

    settlement = models.ForeignKey(
        Settlement,
        on_delete=models.CASCADE,
        related_name='items'
    )

    sub_order = models.OneToOneField(
        'orders.SubOrder',
        on_delete=models.CASCADE,
        related_name='settlement_item'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)
class Refund(models.Model):
    refund_id = models.AutoField(primary_key=True)

    sub_order = models.ForeignKey(
        'orders.SubOrder',
        on_delete=models.CASCADE,
        related_name='refunds'
    )

    settlement_item = models.ForeignKey(
        'settlements.SettlementItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refunds'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    reason = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Chờ xử lý'),
            ('approved', 'Đã duyệt'),
            ('paid', 'Đã hoàn'),
            ('rejected', 'Từ chối'),
        ],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
