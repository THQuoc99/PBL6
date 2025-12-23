# Generated migration to fix old 'paid' status to 'pending'
from django.db import migrations


def fix_paid_status(apps, schema_editor):
    """Convert old 'paid' status to 'pending' since we removed 'paid' from STATUS_CHOICES"""
    Order = apps.get_model('orders', 'Order')
    SubOrder = apps.get_model('orders', 'SubOrder')
    
    # Update Order with status='paid' to 'pending'
    updated_orders = Order.objects.filter(status='paid').update(status='pending')
    print(f"✅ Fixed {updated_orders} Orders with status='paid' → 'pending'")
    
    # Update SubOrder with status='paid' to 'pending'
    updated_suborders = SubOrder.objects.filter(status='paid').update(status='pending')
    print(f"✅ Fixed {updated_suborders} SubOrders with status='paid' → 'pending'")


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_status_alter_suborder_status'),
    ]

    operations = [
        migrations.RunPython(fix_paid_status),
    ]
