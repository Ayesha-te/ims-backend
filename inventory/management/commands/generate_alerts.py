from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from inventory.models import Product, ExpiryAlert


class Command(BaseCommand):
    help = 'Generate expiry alerts for products expiring soon'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days ahead to check for expiring products (default: 30)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regenerate all alerts (delete existing ones)',
        )

    def handle(self, *args, **options):
        alert_days = options['days']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(f'🔍 Checking for products expiring within {alert_days} days...')
        )

        today = timezone.now().date()
        future_date = today + timedelta(days=alert_days)

        if force:
            # Delete existing alerts
            deleted_count = ExpiryAlert.objects.all().delete()[0]
            self.stdout.write(
                self.style.WARNING(f'🗑️ Deleted {deleted_count} existing alerts')
            )

        # Find expiring products
        expiring_products = Product.objects.filter(
            expiry_date__lte=future_date,
            expiry_date__gt=today,
            is_halal=True,
            is_active=True
        )

        # Find expired products
        expired_products = Product.objects.filter(
            expiry_date__lt=today,
            is_halal=True,
            is_active=True
        )

        alerts_created = 0

        # Create alerts for expiring products
        for product in expiring_products:
            alert, created = ExpiryAlert.objects.get_or_create(
                product=product,
                alert_type='EXPIRING_SOON',
                defaults={'is_read': False}
            )
            if created:
                alerts_created += 1
                days_until_expiry = (product.expiry_date - today).days
                self.stdout.write(f'  ⚠️ {product.name} expires in {days_until_expiry} days')

        # Create alerts for expired products
        for product in expired_products:
            alert, created = ExpiryAlert.objects.get_or_create(
                product=product,
                alert_type='EXPIRED',
                defaults={'is_read': False}
            )
            if created:
                alerts_created += 1
                days_expired = (today - product.expiry_date).days
                self.stdout.write(f'  🚨 {product.name} expired {days_expired} days ago')

        self.stdout.write(
            self.style.SUCCESS(f'✅ Generated {alerts_created} new alerts')
        )
        
        # Summary
        total_expiring = expiring_products.count()
        total_expired = expired_products.count()
        total_alerts = ExpiryAlert.objects.filter(is_read=False).count()
        
        self.stdout.write('')
        self.stdout.write('📊 Alert Summary:')
        self.stdout.write(f'   • Products expiring soon: {total_expiring}')
        self.stdout.write(f'   • Products expired: {total_expired}')
        self.stdout.write(f'   • Total unread alerts: {total_alerts}')