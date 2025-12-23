from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from users.models import User
from discount.models import Voucher
from notifications.utils import notify_promotion_expiring


class Command(BaseCommand):
    help = 'Send notifications for promotions that are expiring soon'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Send notifications for promotions expiring within this many hours'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of users to notify per promotion'
        )

    def handle(self, *args, **options):
        hours_ahead = options['hours']
        limit_per_promo = options['limit']
        
        # Calculate expiration threshold
        now = timezone.now()
        expiration_threshold = now + timedelta(hours=hours_ahead)
        
        # Find active vouchers expiring soon
        expiring_vouchers = Voucher.objects.filter(
            is_active=True,
            end_date__lte=expiration_threshold.date(),
            end_date__gte=now.date()
        ).select_related('seller')
        
        total_notifications = 0
        
        for voucher in expiring_vouchers:
            # Calculate hours left
            end_datetime = timezone.datetime.combine(
                voucher.end_date, 
                timezone.datetime.max.time()
            ).replace(tzinfo=timezone.get_current_timezone())
            hours_left = max(1, int((end_datetime - now).total_seconds() / 3600))
            
            # Get users to notify (in real app, this would be voucher holders or interested users)
            users_to_notify = User.objects.filter(is_active=True)[:limit_per_promo]
            
            if users_to_notify.exists():
                promotion_name = f"Giảm {voucher.discount_value}%" if voucher.discount_type == 'percent' else f"Giảm {voucher.discount_value}đ"
                
                for user in users_to_notify:
                    try:
                        notify_promotion_expiring(user, promotion_name, hours_left)
                        total_notifications += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Failed to notify user {user.username}: {str(e)}')
                        )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Sent {len(users_to_notify)} notifications for voucher "{voucher.code}" '
                        f'(expires in {hours_left} hours)'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Total notifications sent: {total_notifications}')
        )