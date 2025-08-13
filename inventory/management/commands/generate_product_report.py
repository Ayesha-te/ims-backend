from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from datetime import timedelta
from inventory.models import Product
import logging
import json

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate a comprehensive product report with statistics'

    def handle(self, *args, **options):
        try:
            today = timezone.now().date()
            thirty_days_from_now = today + timedelta(days=30)
            
            # Get statistics
            total_products = Product.objects.filter(is_halal=True, is_active=True).count()
            expired_products = Product.objects.filter(
                expiry_date__lt=today,
                is_halal=True,
                is_active=True
            ).count()
            expiring_soon = Product.objects.filter(
                expiry_date__lte=thirty_days_from_now,
                expiry_date__gt=today,
                is_halal=True,
                is_active=True
            ).count()
            low_stock_products = Product.objects.filter(
                current_stock__lte=models.F('minimum_stock'),
                is_halal=True,
                is_active=True
            ).count()
            
            report_data = {
                'generated_at': today.isoformat(),
                'total_products': total_products,
                'expired_products': expired_products,
                'expiring_soon': expiring_soon,
                'low_stock_products': low_stock_products,
            }
            
            message = f"Product Report Generated: {json.dumps(report_data, indent=2)}"
            self.stdout.write(self.style.SUCCESS(message))
            logger.info(message)
            
        except Exception as e:
            error_message = f"Error generating product report: {str(e)}"
            self.stdout.write(self.style.ERROR(error_message))
            logger.error(error_message)
            raise