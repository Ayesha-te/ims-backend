from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.db import models
from .models import Product, ExpiryAlert
import logging

logger = logging.getLogger(__name__)

def generate_expiry_alerts():
    """
    Generate expiry alerts for products that are expiring soon or expired.
    This function is called by the generate_alerts management command.
    """
    try:
        today = timezone.now().date()
        alert_days = getattr(settings, 'INVENTORY_SETTINGS', {}).get('EXPIRY_ALERT_DAYS', 30)
        thirty_days_from_now = today + timedelta(days=alert_days)
        
        alerts_created = 0
        
        # Get products that are expiring soon (within 30 days)
        expiring_products = Product.objects.filter(
            expiry_date__lte=thirty_days_from_now,
            expiry_date__gt=today,
            is_halal=True,
            is_active=True
        )
        
        # Get expired products
        expired_products = Product.objects.filter(
            expiry_date__lt=today,
            is_halal=True,
            is_active=True
        )
        
        # Create alerts for expiring products
        for product in expiring_products:
            alert, created = ExpiryAlert.objects.get_or_create(
                product=product,
                alert_type='EXPIRING_SOON',
                defaults={'is_read': False}
            )
            if created:
                alerts_created += 1
                logger.info(f"Created expiring soon alert for product: {product.name}")
        
        # Create alerts for expired products
        for product in expired_products:
            alert, created = ExpiryAlert.objects.get_or_create(
                product=product,
                alert_type='EXPIRED',
                defaults={'is_read': False}
            )
            if created:
                alerts_created += 1
                logger.info(f"Created expired alert for product: {product.name}")
        
        logger.info(f"Generated {alerts_created} new expiry alerts")
        return f"Generated {alerts_created} new expiry alerts"
        
    except Exception as e:
        logger.error(f"Error generating expiry alerts: {str(e)}")
        raise


def cleanup_old_alerts():
    """
    Clean up old read alerts that are older than 30 days.
    This function is called by the cleanup_old_alerts management command.
    """
    try:
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Delete old read alerts
        deleted_count = ExpiryAlert.objects.filter(
            is_read=True,
            created_at__lt=thirty_days_ago
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old alerts")
        return f"Cleaned up {deleted_count} old alerts"
        
    except Exception as e:
        logger.error(f"Error cleaning up old alerts: {str(e)}")
        raise


def update_product_stock(product_id, transaction_type, quantity, user_id, reason=""):
    """
    Function to update product stock and create transaction record.
    Can be called directly or from management commands.
    """
    try:
        from django.contrib.auth.models import User
        from .models import Product, StockTransaction
        
        product = Product.objects.get(id=product_id, is_halal=True, is_active=True)
        user = User.objects.get(id=user_id)
        
        previous_stock = product.current_stock
        
        if transaction_type == 'IN':
            product.current_stock += quantity
        elif transaction_type == 'OUT':
            if product.current_stock < quantity:
                raise ValueError(f"Insufficient stock. Available: {product.current_stock}, Requested: {quantity}")
            product.current_stock -= quantity
        elif transaction_type == 'ADJUSTMENT':
            product.current_stock = quantity
        
        product.save()
        
        # Create stock transaction record
        StockTransaction.objects.create(
            product=product,
            transaction_type=transaction_type,
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=product.current_stock,
            reason=reason,
            user=user
        )
        
        logger.info(f"Updated stock for product {product.name}: {previous_stock} -> {product.current_stock}")
        return f"Stock updated successfully for {product.name}"
        
    except Exception as e:
        logger.error(f"Error updating product stock: {str(e)}")
        raise


def generate_product_report():
    """
    Generate a comprehensive product report with statistics.
    This function is called by the generate_product_report management command.
    """
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
        
        logger.info(f"Generated product report: {report_data}")
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating product report: {str(e)}")
        raise


def bulk_update_products(product_updates):
    """
    Function for bulk updating products.
    Useful for importing large datasets or batch operations.
    """
    try:
        updated_count = 0
        
        for update_data in product_updates:
            try:
                product_id = update_data['id']
                product = Product.objects.get(id=product_id, is_halal=True, is_active=True)
                
                # Update fields if provided
                for field, value in update_data.get('updates', {}).items():
                    if hasattr(product, field):
                        setattr(product, field, value)
                
                product.save()
                updated_count += 1
                
            except Product.DoesNotExist:
                logger.warning(f"Product with id {product_id} not found")
                continue
            except Exception as e:
                logger.error(f"Error updating product {product_id}: {str(e)}")
                continue
        
        logger.info(f"Bulk updated {updated_count} products")
        return f"Bulk updated {updated_count} products"
        
    except Exception as e:
        logger.error(f"Error in bulk update: {str(e)}")
        raise