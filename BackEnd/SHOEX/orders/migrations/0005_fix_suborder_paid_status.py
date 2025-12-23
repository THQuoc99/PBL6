# Generated migration to fix old 'paid' status in SubOrder table
from django.db import migrations


def fix_suborder_paid_status(apps, schema_editor):
    """Convert old 'paid' status to 'processing' in SubOrder table"""
    SubOrder = apps.get_model('orders', 'SubOrder')
    
    # Update SubOrder with status='paid' to 'processing'
    updated = SubOrder.objects.filter(status='paid').update(status='processing')
    print(f"✅ Fixed {updated} SubOrders with status='paid' → 'processing'")


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_fix_paid_status'),
    ]

    operations = [
        migrations.RunPython(fix_suborder_paid_status),
    ]
