from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Category, Supplier, Product, StockTransaction, ExpiryAlert, 
    ProductTicket, Supermarket, Substore, ExcelImport, ImageImport
)


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
    store_location = serializers.ReadOnlyField()
    parent_supermarket_name = serializers.CharField(source='parent_supermarket.name', read_only=True)
    substore_name = serializers.CharField(source='substore.name', read_only=True)
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


class SupermarketSerializer(serializers.ModelSerializer):
    """Serializer for Supermarket model"""
    total_products = serializers.ReadOnlyField()
    total_stock_value = serializers.ReadOnlyField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Supermarket
        fields = [
            'id', 'name', 'address', 'phone', 'email', 'description', 
            'logo', 'registration_date', 'is_verified', 'verified_at', 
            'is_active', 'total_products', 'total_stock_value', 'user_email'
        ]
        read_only_fields = ['id', 'registration_date', 'is_verified', 'verified_at']


class SupermarketRegistrationSerializer(serializers.Serializer):
    """Serializer for supermarket registration"""
    name = serializers.CharField(max_length=200)
    address = serializers.CharField()
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    description = serializers.CharField(required=False, allow_blank=True)
    logo = serializers.URLField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Check if user with this email already exists
        if User.objects.filter(username=data['email']).exists():
            raise serializers.ValidationError("A user with this email already exists")
        
        return data


class SubstoreSerializer(serializers.ModelSerializer):
    """Serializer for Substore model"""
    supermarket_name = serializers.CharField(source='supermarket.name', read_only=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    total_products = serializers.ReadOnlyField()
    total_stock_value = serializers.ReadOnlyField()
    
    class Meta:
        model = Substore
        fields = [
            'id', 'name', 'address', 'phone', 'email', 'description',
            'supermarket', 'supermarket_name', 'manager', 'manager_name',
            'created_date', 'is_active', 'total_products', 'total_stock_value'
        ]
        read_only_fields = ['id', 'created_date']


class SubstoreCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating substores"""
    
    class Meta:
        model = Substore
        fields = ['name', 'address', 'phone', 'email', 'description', 'manager']
    
    def validate_name(self, value):
        # Check if substore name is unique within the supermarket
        supermarket = self.context['supermarket']
        if Substore.objects.filter(supermarket=supermarket, name=value).exists():
            raise serializers.ValidationError("A substore with this name already exists in your supermarket.")
        return value


class ExcelImportSerializer(serializers.ModelSerializer):
    """Serializer for Excel imports"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    supermarket_name = serializers.CharField(source='supermarket.name', read_only=True)
    substore_name = serializers.CharField(source='substore.name', read_only=True)
    
    class Meta:
        model = ExcelImport
        fields = [
            'id', 'batch_id', 'file_name', 'uploaded_by', 'uploaded_by_name',
            'supermarket', 'supermarket_name', 'substore', 'substore_name',
            'status', 'total_rows', 'processed_rows', 'successful_imports',
            'failed_imports', 'error_log', 'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'batch_id', 'uploaded_by', 'status', 'total_rows', 
            'processed_rows', 'successful_imports', 'failed_imports', 
            'error_log', 'created_at', 'started_at', 'completed_at'
        ]


class ExcelImportCreateSerializer(serializers.Serializer):
    """Serializer for creating Excel imports"""
    file_name = serializers.CharField(max_length=255)
    file_data = serializers.CharField()  # Base64 encoded file
    target_store = serializers.ChoiceField(choices=['supermarket', 'substore'])
    substore_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate(self, data):
        if data['target_store'] == 'substore' and not data.get('substore_id'):
            raise serializers.ValidationError("Substore ID is required when target store is substore.")
        return data


class ImageImportSerializer(serializers.ModelSerializer):
    """Serializer for Image imports"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    supermarket_name = serializers.CharField(source='supermarket.name', read_only=True)
    substore_name = serializers.CharField(source='substore.name', read_only=True)
    
    class Meta:
        model = ImageImport
        fields = [
            'id', 'batch_id', 'image_name', 'uploaded_by', 'uploaded_by_name',
            'supermarket', 'supermarket_name', 'substore', 'substore_name',
            'status', 'extracted_text', 'extracted_data', 'error_log',
            'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'batch_id', 'uploaded_by', 'status', 'extracted_text',
            'extracted_data', 'error_log', 'created_at', 'started_at', 'completed_at'
        ]


class ImageImportCreateSerializer(serializers.Serializer):
    """Serializer for creating Image imports"""
    image_name = serializers.CharField(max_length=255)
    image_data = serializers.CharField()  # Base64 encoded image
    target_store = serializers.ChoiceField(choices=['supermarket', 'substore'])
    substore_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate(self, data):
        if data['target_store'] == 'substore' and not data.get('substore_id'):
            raise serializers.ValidationError("Substore ID is required when target store is substore.")
        return data


class ProductBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk product creation from Excel/Image"""
    products_data = serializers.ListField(child=serializers.DictField())
    target_store = serializers.ChoiceField(choices=['supermarket', 'substore'])
    substore_id = serializers.IntegerField(required=False, allow_null=True)
    import_batch_id = serializers.CharField(max_length=100)
    
    def validate(self, data):
        if data['target_store'] == 'substore' and not data.get('substore_id'):
            raise serializers.ValidationError("Substore ID is required when target store is substore.")
        return data


class ProductMultiStoreCreateSerializer(serializers.Serializer):
    """Serializer for creating products in multiple stores"""
    product_data = serializers.DictField()
    target_stores = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of store objects with 'type' and 'id' fields"
    )
    add_to_all_stores = serializers.BooleanField(default=False)
    
    def validate_product_data(self, value):
        """Validate product data structure"""
        required_fields = ['name', 'category', 'supplier', 'sku', 'price', 'cost_price']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Product data must include '{field}' field")
        return value
    
    def validate_target_stores(self, value):
        """Validate target stores structure"""
        if value:
            for store in value:
                if 'type' not in store or 'id' not in store:
                    raise serializers.ValidationError("Each target store must have 'type' and 'id' fields")
                if store['type'] not in ['supermarket', 'substore']:
                    raise serializers.ValidationError("Store type must be 'supermarket' or 'substore'")
        return value
    
    def validate(self, data):
        if not data.get('add_to_all_stores') and not data.get('target_stores'):
            raise serializers.ValidationError("Either 'add_to_all_stores' must be True or 'target_stores' must be provided")
        return data


class EnhancedExcelImportCreateSerializer(serializers.Serializer):
    """Enhanced serializer for Excel imports with multi-store support"""
    file_name = serializers.CharField(max_length=255)
    file_data = serializers.CharField()  # Base64 encoded file
    target_stores = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of store objects with 'type' and 'id' fields"
    )
    add_to_all_stores = serializers.BooleanField(default=False)
    
    def validate(self, data):
        if not data.get('add_to_all_stores') and not data.get('target_stores'):
            raise serializers.ValidationError("Either 'add_to_all_stores' must be True or 'target_stores' must be provided")
        return data


class EnhancedImageImportCreateSerializer(serializers.Serializer):
    """Enhanced serializer for Image imports with multi-store support"""
    image_name = serializers.CharField(max_length=255)
    image_data = serializers.CharField()  # Base64 encoded image
    target_stores = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of store objects with 'type' and 'id' fields"
    )
    add_to_all_stores = serializers.BooleanField(default=False)
    
    def validate(self, data):
        if not data.get('add_to_all_stores') and not data.get('target_stores'):
            raise serializers.ValidationError("Either 'add_to_all_stores' must be True or 'target_stores' must be provided")
        return data


class POSProductSyncSerializer(serializers.Serializer):
    """Serializer for POS product synchronization"""
    id = serializers.UUIDField()
    sku = serializers.CharField()
    name = serializers.CharField()
    barcode = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    cost_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    current_stock = serializers.IntegerField()
    category = serializers.CharField()
    supplier = serializers.CharField()
    is_halal = serializers.BooleanField()
    store_location = serializers.CharField()
    store_type = serializers.CharField()
    store_id = serializers.IntegerField()
    last_updated = serializers.DateTimeField()


class POSStockUpdateSerializer(serializers.Serializer):
    """Serializer for POS stock updates"""
    updates = serializers.ListField(
        child=serializers.DictField()
    )
    
    def validate_updates(self, value):
        """Validate stock update structure"""
        for update in value:
            required_fields = ['product_id', 'new_stock']
            for field in required_fields:
                if field not in update:
                    raise serializers.ValidationError(f"Each update must include '{field}' field")
        return value


class POSSalesDataSerializer(serializers.Serializer):
    """Serializer for POS sales data"""
    sales = serializers.ListField(
        child=serializers.DictField()
    )
    
    def validate_sales(self, value):
        """Validate sales data structure"""
        for sale in value:
            required_fields = ['product_id', 'quantity_sold']
            for field in required_fields:
                if field not in sale:
                    raise serializers.ValidationError(f"Each sale must include '{field}' field")
        return value