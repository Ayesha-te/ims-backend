from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count, F
from django.db import models
from django.utils import timezone
from datetime import timedelta, date
from .models import (
    Category, Supplier, Product, StockTransaction, 
    ExpiryAlert, ProductTicket, Supermarket
)
from .serializers import (
    CategorySerializer, SupplierSerializer, ProductSerializer,
    ProductCreateSerializer, StockTransactionSerializer, ExpiryAlertSerializer,
    ProductTicketSerializer, BarcodeSearchSerializer, StockUpdateSerializer,
    DashboardStatsSerializer, SupermarketSerializer
)
import json


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def halal_certified(self, request):
        """Get only Halal certified suppliers"""
        suppliers = self.queryset.filter(halal_certified=True)
        serializer = self.get_serializer(suppliers, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only show products belonging to the current supermarket
        try:
            supermarket = Supermarket.objects.get(user=self.request.user)
            return Product.objects.filter(supermarket=supermarket, is_halal=True, is_active=True)
        except Supermarket.DoesNotExist:
            # For users without supermarket profiles, show all products (admin view)
            if self.request.user.is_superuser:
                return Product.objects.filter(is_halal=True, is_active=True)
            return Product.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer
    
    def perform_create(self, serializer):
        # Automatically assign the product to the current user's supermarket
        try:
            supermarket = Supermarket.objects.get(user=self.request.user)
            serializer.save(supermarket=supermarket)
        except Supermarket.DoesNotExist:
            if self.request.user.is_superuser:
                serializer.save()  # Admin can create products without supermarket
            else:
                raise serializers.ValidationError("You must be registered as a supermarket to create products")
    
    @action(detail=False, methods=['post'])
    def scan_barcode(self, request):
        """Scan barcode or QR code to find product"""
        serializer = BarcodeSearchSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            scan_type = serializer.validated_data['scan_type']
            
            try:
                if scan_type == 'BARCODE':
                    product = Product.objects.get(barcode=code, is_halal=True, is_active=True)
                else:  # QR_CODE
                    # Parse QR code data (assuming it contains product ID or barcode)
                    try:
                        qr_data = json.loads(code.replace("'", '"'))
                        product_id = qr_data.get('id')
                        barcode = qr_data.get('barcode')
                        
                        if product_id:
                            product = Product.objects.get(id=product_id, is_halal=True, is_active=True)
                        elif barcode:
                            product = Product.objects.get(barcode=barcode, is_halal=True, is_active=True)
                        else:
                            return Response({'error': 'Invalid QR code format'}, 
                                          status=status.HTTP_400_BAD_REQUEST)
                    except (json.JSONDecodeError, ValueError):
                        # Try as direct barcode search
                        product = Product.objects.get(barcode=code, is_halal=True, is_active=True)
                
                product_serializer = ProductSerializer(product)
                return Response({
                    'product': product_serializer.data,
                    'scan_successful': True,
                    'message': f'Halal product found: {product.name}'
                })
                
            except Product.DoesNotExist:
                return Response({
                    'error': 'Product not found or not Halal certified',
                    'scan_successful': False,
                    'message': 'This product is not in our Halal inventory'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get products expiring within 30 days"""
        thirty_days_from_now = timezone.now().date() + timedelta(days=30)
        products = self.queryset.filter(
            expiry_date__lte=thirty_days_from_now,
            expiry_date__gt=timezone.now().date()
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get expired products"""
        products = self.queryset.filter(expiry_date__lt=timezone.now().date())
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        products = self.queryset.filter(current_stock__lte=F('minimum_stock'))
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update product stock"""
        product = get_object_or_404(Product, pk=pk, is_halal=True, is_active=True)
        serializer = StockUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            transaction_type = serializer.validated_data['transaction_type']
            quantity = serializer.validated_data['quantity']
            reason = serializer.validated_data.get('reason', '')
            
            previous_stock = product.current_stock
            
            if transaction_type == 'IN':
                product.current_stock += quantity
            elif transaction_type == 'OUT':
                if product.current_stock < quantity:
                    return Response({
                        'error': 'Insufficient stock',
                        'available_stock': product.current_stock
                    }, status=status.HTTP_400_BAD_REQUEST)
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
                user=request.user
            )
            
            product_serializer = ProductSerializer(product)
            return Response({
                'product': product_serializer.data,
                'message': 'Stock updated successfully'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def generate_ticket(self, request, pk=None):
        """Generate product ticket/label"""
        product = get_object_or_404(Product, pk=pk, is_halal=True, is_active=True)
        
        ticket_data = {
            'product_name': product.name,
            'sku': product.sku,
            'barcode': product.barcode,
            'barcode_image': product.barcode_image,
            'qr_code_image': product.qr_code_image,
            'price': str(product.price),
            'expiry_date': product.expiry_date.strftime('%Y-%m-%d') if product.expiry_date else None,
            'halal_status': 'HALAL CERTIFIED',
            'category': product.category.name,
            'supplier': product.supplier.name,
            'generated_at': timezone.now().isoformat()
        }
        
        ticket = ProductTicket.objects.create(
            product=product,
            ticket_data=ticket_data,
            created_by=request.user
        )
        
        serializer = ProductTicketSerializer(ticket)
        return Response(serializer.data)


class StockTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockTransaction.objects.all()
    serializer_class = StockTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            queryset = queryset.filter(product__id=product_id)
        return queryset.order_by('-created_at')


class ExpiryAlertViewSet(viewsets.ModelViewSet):
    queryset = ExpiryAlert.objects.all()
    serializer_class = ExpiryAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().filter(is_read=False).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark alert as read"""
        alert = get_object_or_404(ExpiryAlert, pk=pk)
        alert.is_read = True
        alert.save()
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all alerts as read"""
        updated = ExpiryAlert.objects.filter(is_read=False).update(is_read=True)
        return Response({'message': f'{updated} alerts marked as read'})
    
    @action(detail=False, methods=['post'])
    def generate_alerts(self, request):
        """Manually generate expiry alerts"""
        thirty_days_from_now = timezone.now().date() + timedelta(days=30)
        today = timezone.now().date()
        
        # Products expiring soon
        expiring_products = Product.objects.filter(
            expiry_date__lte=thirty_days_from_now,
            expiry_date__gt=today,
            is_halal=True,
            is_active=True
        )
        
        # Expired products
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
                alert_type='EXPIRING_SOON'
            )
            if created:
                alerts_created += 1
        
        # Create alerts for expired products
        for product in expired_products:
            alert, created = ExpiryAlert.objects.get_or_create(
                product=product,
                alert_type='EXPIRED'
            )
            if created:
                alerts_created += 1
        
        return Response({
            'message': f'{alerts_created} new alerts created',
            'expiring_soon_count': expiring_products.count(),
            'expired_count': expired_products.count()
        })


class ProductTicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductTicket.objects.all()
    serializer_class = ProductTicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            queryset = queryset.filter(product__id=product_id)
        return queryset.order_by('-created_at')


class SupermarketViewSet(viewsets.ModelViewSet):
    queryset = Supermarket.objects.all()
    serializer_class = SupermarketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Regular users can only see their own supermarket
        # Superusers can see all supermarkets
        if self.request.user.is_superuser:
            return Supermarket.objects.all()
        
        try:
            supermarket = Supermarket.objects.get(user=self.request.user)
            return Supermarket.objects.filter(id=supermarket.id)
        except Supermarket.DoesNotExist:
            return Supermarket.objects.none()
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a supermarket (admin only)"""
        if not request.user.is_superuser:
            return Response({'error': 'Only admins can verify supermarkets'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        supermarket = get_object_or_404(Supermarket, pk=pk)
        supermarket.is_verified = True
        supermarket.verified_by = request.user
        supermarket.verified_at = timezone.now()
        supermarket.save()
        
        serializer = self.get_serializer(supermarket)
        return Response({
            'message': f'Supermarket {supermarket.name} has been verified',
            'supermarket': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def verified(self, request):
        """Get only verified supermarkets"""
        queryset = self.get_queryset().filter(is_verified=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DashboardViewSet(viewsets.ViewSet):
    """Dashboard statistics and overview"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get dashboard statistics"""
        today = timezone.now().date()
        thirty_days_from_now = today + timedelta(days=30)
        
        # Basic counts
        total_products = Product.objects.filter(is_halal=True, is_active=True).count()
        total_halal_products = total_products  # Since we only show Halal products
        
        # Stock-related stats
        products = Product.objects.filter(is_halal=True, is_active=True)
        low_stock_products = products.filter(current_stock__lte=F('minimum_stock')).count()
        
        # Expiry-related stats
        expiring_soon_products = products.filter(
            expiry_date__lte=thirty_days_from_now,
            expiry_date__gt=today
        ).count()
        expired_products = products.filter(expiry_date__lt=today).count()
        
        # Stock value
        total_stock_value = products.aggregate(
            total=Sum(F('current_stock') * F('cost_price'))
        )['total'] or 0
        
        # Categories and suppliers
        categories_count = Category.objects.count()
        suppliers_count = Supplier.objects.filter(halal_certified=True).count()
        
        # Stock status breakdown
        stock_stats = {
            'out_of_stock_count': products.filter(current_stock=0).count(),
            'low_stock_count': products.filter(
                current_stock__lte=F('minimum_stock'),
                current_stock__gt=0
            ).count(),
            'normal_stock_count': products.filter(
                current_stock__gt=F('minimum_stock'),
                current_stock__lt=F('maximum_stock')
            ).count(),
            'overstock_count': products.filter(
                current_stock__gte=F('maximum_stock')
            ).count(),
        }
        
        # Recent activities
        recent_transactions = StockTransaction.objects.select_related('product', 'user')[:10]
        recent_alerts = ExpiryAlert.objects.select_related('product').filter(is_read=False)[:10]
        
        stats_data = {
            'total_products': total_products,
            'total_halal_products': total_halal_products,
            'low_stock_products': low_stock_products,
            'expiring_soon_products': expiring_soon_products,
            'expired_products': expired_products,
            'total_stock_value': total_stock_value,
            'categories_count': categories_count,
            'suppliers_count': suppliers_count,
            **stock_stats,
            'recent_stock_transactions': StockTransactionSerializer(recent_transactions, many=True).data,
            'recent_expiry_alerts': ExpiryAlertSerializer(recent_alerts, many=True).data
        }
        
        return Response(stats_data)
    
    @action(detail=False, methods=['get'])
    def alerts_summary(self, request):
        """Get alerts summary for dashboard"""
        today = timezone.now().date()
        
        # Get unread alerts grouped by type
        expiring_alerts = ExpiryAlert.objects.filter(
            alert_type='EXPIRING_SOON',
            is_read=False
        ).select_related('product')
        
        expired_alerts = ExpiryAlert.objects.filter(
            alert_type='EXPIRED',
            is_read=False
        ).select_related('product')
        
        return Response({
            'expiring_soon': {
                'count': expiring_alerts.count(),
                'alerts': ExpiryAlertSerializer(expiring_alerts[:5], many=True).data
            },
            'expired': {
                'count': expired_alerts.count(),
                'alerts': ExpiryAlertSerializer(expired_alerts[:5], many=True).data
            },
            'total_unread': expiring_alerts.count() + expired_alerts.count()
        })