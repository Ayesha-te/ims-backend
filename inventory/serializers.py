from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Supplier, Product, StockTransaction, ExpiryAlert, ProductTicket


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    is_expiring_soon = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    stock_status = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def validate(self, data):
        # Only allow Halal products
        if not data.get('is_halal', False):
            raise serializers.ValidationError("Only Halal products are allowed in this system.")
        
        # Validate stock levels
        if data.get('minimum_stock', 0) > data.get('maximum_stock', 1000):
            raise serializers.ValidationError("Minimum stock cannot be greater than maximum stock.")
        
        # Validate dates
        if data.get('manufacturing_date') and data.get('expiry_date'):
            if data['manufacturing_date'] >= data['expiry_date']:
                raise serializers.ValidationError("Manufacturing date must be before expiry date.")
        
        return data


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating products with ticket generation"""
    generate_ticket = serializers.BooleanField(default=True, write_only=True)
    
    class Meta:
        model = Product
        exclude = ['barcode_image', 'qr_code_image']
    
    def create(self, validated_data):
        generate_ticket = validated_data.pop('generate_ticket', True)
        product = super().create(validated_data)
        
        # Generate ticket if requested
        if generate_ticket:
            self.create_product_ticket(product)
        
        return product
    
    def create_product_ticket(self, product):
        """Create a product ticket/label"""
        ticket_data = {
            'product_name': product.name,
            'sku': product.sku,
            'barcode': product.barcode,
            'barcode_image': product.barcode_image,
            'qr_code_image': product.qr_code_image,
            'price': str(product.price),
            'expiry_date': product.expiry_date.strftime('%Y-%m-%d') if product.expiry_date else None,
            'halal_status': 'HALAL CERTIFIED' if product.is_halal else 'NOT HALAL',
            'category': product.category.name,
            'supplier': product.supplier.name,
            'generated_at': product.created_at.isoformat()
        }
        
        ProductTicket.objects.create(
            product=product,
            ticket_data=ticket_data,
            created_by=self.context['request'].user
        )


class StockTransactionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = StockTransaction
        fields = '__all__'


class ExpiryAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    expiry_date = serializers.DateField(source='product.expiry_date', read_only=True)
    days_until_expiry = serializers.ReadOnlyField(source='product.days_until_expiry')
    current_stock = serializers.IntegerField(source='product.current_stock', read_only=True)
    
    class Meta:
        model = ExpiryAlert
        fields = '__all__'


class ProductTicketSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ProductTicket
        fields = '__all__'


class BarcodeSearchSerializer(serializers.Serializer):
    """Serializer for barcode/QR code search"""
    code = serializers.CharField(max_length=200)
    scan_type = serializers.ChoiceField(choices=['BARCODE', 'QR_CODE'], default='BARCODE')


class StockUpdateSerializer(serializers.Serializer):
    """Serializer for stock updates"""
    product_id = serializers.UUIDField()
    transaction_type = serializers.ChoiceField(choices=StockTransaction.TRANSACTION_TYPES)
    quantity = serializers.IntegerField()
    reason = serializers.CharField(max_length=200, required=False)


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_products = serializers.IntegerField()
    total_halal_products = serializers.IntegerField()
    low_stock_products = serializers.IntegerField()
    expiring_soon_products = serializers.IntegerField()
    expired_products = serializers.IntegerField()
    total_stock_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    categories_count = serializers.IntegerField()
    suppliers_count = serializers.IntegerField()
    
    # Stock status breakdown
    out_of_stock_count = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    normal_stock_count = serializers.IntegerField()
    overstock_count = serializers.IntegerField()
    
    # Recent activities
    recent_stock_transactions = StockTransactionSerializer(many=True)
    recent_expiry_alerts = ExpiryAlertSerializer(many=True)