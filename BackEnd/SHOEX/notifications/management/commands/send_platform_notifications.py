from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from notifications.utils import (
    notify_platform_flash_sale,
    notify_platform_announcement,
    notify_promotion_expiring
)


class Command(BaseCommand):
    help = 'Send platform notifications (flash sales, announcements, expiring promotions)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['flash_sale', 'announcement', 'expiring_promotions', 'all'],
            default='all',
            help='Type of notification to send'
        )
        parser.add_argument(
            '--title',
            type=str,
            help='Title for flash sale or announcement'
        )
        parser.add_argument(
            '--message',
            type=str,
            help='Message for announcement'
        )
        parser.add_argument(
            '--discount',
            type=str,
            help='Discount percentage for flash sale (e.g., "70")'
        )

    def handle(self, *args, **options):
        notification_type = options['type']
        all_users = User.objects.filter(is_active=True)[:100]  # Limit for testing

        if notification_type in ['flash_sale', 'all']:
            if options['title'] and options['discount']:
                self.send_flash_sale_notification(options['title'], options['discount'], all_users)
            else:
                self.stdout.write(
                    self.style.WARNING('Flash sale requires --title and --discount arguments')
                )

        if notification_type in ['announcement', 'all']:
            if options['title'] and options['message']:
                self.send_announcement_notification(options['title'], options['message'], all_users)
            else:
                self.stdout.write(
                    self.style.WARNING('Announcement requires --title and --message arguments')
                )

        if notification_type in ['expiring_promotions', 'all']:
            self.send_expiring_promotions_notifications(all_users)

    def send_flash_sale_notification(self, title, discount, users):
        """Send flash sale notification to all users"""
        try:
            notify_platform_flash_sale(users, title, discount)
            self.stdout.write(
                self.style.SUCCESS(f'Sent flash sale notification "{title}" to {len(users)} users')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send flash sale notification: {str(e)}')
            )

    def send_announcement_notification(self, title, message, users):
        """Send platform announcement to all users"""
        try:
            notify_platform_announcement(users, title, message)
            self.stdout.write(
                self.style.SUCCESS(f'Sent announcement "{title}" to {len(users)} users')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send announcement: {str(e)}')
            )

    def send_expiring_promotions_notifications(self, users):
        """Send notifications for promotions expiring soon"""
        # This is a placeholder - in real implementation, you'd query actual promotions
        # For now, just send a sample notification
        try:
            for user in users[:5]:  # Send to first 5 users as example
                notify_promotion_expiring(user, "Flash Sale 12h", 2)
            self.stdout.write(
                self.style.SUCCESS('Sent expiring promotion notifications to sample users')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send expiring promotion notifications: {str(e)}')
            )