from django.core.management.base import BaseCommand
from users.models import User
from notifications.utils import (
    notify_order_created,
    notify_order_status_update,
    notify_shop_new_product,
    notify_shop_promotion,
    notify_platform_flash_sale,
    notify_platform_voucher,
    notify_platform_announcement,
    notify_promotion_expiring
)


class Command(BaseCommand):
    help = 'Test all notification functions with sample data'

    def handle(self, *args, **options):
        # Get sample users
        users = list(User.objects.filter(is_active=True)[:5])
        if not users:
            self.stdout.write(self.style.ERROR('No active users found for testing'))
            return

        sample_user = users[0]
        
        self.stdout.write(self.style.SUCCESS('Testing all notification functions...\n'))

        # Test order notifications
        self.stdout.write('1. Testing order notifications...')
        try:
            notify_order_created(sample_user, 12345)
            self.stdout.write(self.style.SUCCESS('   ✓ Order created notification'))
            
            notify_order_status_update(sample_user, 12345, 'confirmed')
            self.stdout.write(self.style.SUCCESS('   ✓ Order status update notification'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Order notifications failed: {str(e)}'))

        # Test shop notifications
        self.stdout.write('\n2. Testing shop notifications...')
        try:
            shop_id_int = hash('SHOP001') % 1000000  # Convert to positive integer
            notify_shop_new_product(users, shop_id_int, 'Nike Official', 'Air Max 2025')
            self.stdout.write(self.style.SUCCESS('   ✓ Shop new product notification'))
            
            notify_shop_promotion(users, shop_id_int, 'Nike Official', 'Flash Sale Giày Thể Thao', '50%')
            self.stdout.write(self.style.SUCCESS('   ✓ Shop promotion notification'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Shop notifications failed: {str(e)}'))

        # Test platform notifications
        self.stdout.write('\n3. Testing platform notifications...')
        try:
            notify_platform_flash_sale(users, 'Flash Sale 12h Trưa', '70%')
            self.stdout.write(self.style.SUCCESS('   ✓ Platform flash sale notification'))
            
            notify_platform_voucher(users, 'FREESHIP100', '100k')
            self.stdout.write(self.style.SUCCESS('   ✓ Platform voucher notification'))
            
            notify_platform_announcement(
                users, 
                'Cập nhật ứng dụng', 
                'Phiên bản mới với nhiều tính năng thú vị đang chờ bạn!'
            )
            self.stdout.write(self.style.SUCCESS('   ✓ Platform announcement notification'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Platform notifications failed: {str(e)}'))

        # Test promotion expiring
        self.stdout.write('\n4. Testing promotion expiring notification...')
        try:
            notify_promotion_expiring(sample_user, 'Flash Sale 12h', 2)
            self.stdout.write(self.style.SUCCESS('   ✓ Promotion expiring notification'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Promotion expiring notification failed: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('\n✅ All notification tests completed!'))
        self.stdout.write('Check the notification list in the app to see the results.')