from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from inventory.models import ExpiryAlert
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up old read alerts that are older than 30 days'

    def handle(self, *args, **options):
        try:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            
            # Delete old read alerts
            deleted_count = ExpiryAlert.objects.filter(
                is_read=True,
                created_at__lt=thirty_days_ago
            ).delete()[0]
            
            message = f"Cleaned up {deleted_count} old alerts"
            self.stdout.write(self.style.SUCCESS(message))
            logger.info(message)
            
        except Exception as e:
            error_message = f"Error cleaning up old alerts: {str(e)}"
            self.stdout.write(self.style.ERROR(error_message))
            logger.error(error_message)
            raise