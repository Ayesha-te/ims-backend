from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import qrcode
from PIL import Image
import base64


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    halal_certified = models.BooleanField(default=False)
    certification_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    # Basic Product Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    
    # Halal Verification
    is_halal = models.BooleanField(default=False)
    halal_certification_number = models.CharField(max_length=100, blank=True)
    halal_verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_products')
    halal_verified_date = models.DateTimeField(null=True, blank=True)
    
    # Product Details
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Stock Information
    current_stock = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=10)
    maximum_stock = models.PositiveIntegerField(default=1000)
    
    # Dates
    manufacturing_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Generated Assets
    barcode_image = models.TextField(blank=True)  # Base64 encoded barcode image
    qr_code_image = models.TextField(blank=True)  # Base64 encoded QR code image
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Generate barcode if not exists
        if not self.barcode:
            self.barcode = f"HALAL{self.sku}"
        
        # Generate barcode and QR code images
        if not self.barcode_image:
            self.barcode_image = self.generate_barcode()
        
        if not self.qr_code_image:
            self.qr_code_image = self.generate_qr_code()
        
        super().save(*args, **kwargs)
    
    def generate_barcode(self):
        """Generate barcode image as base64 string"""
        try:
            # Create barcode
            code128 = barcode.get_barcode_class('code128')
            barcode_instance = code128(self.barcode, writer=ImageWriter())
            
            # Save to BytesIO
            buffer = BytesIO()
            barcode_instance.write(buffer)
            
            # Convert to base64
            buffer.seek(0)
            barcode_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/png;base64,{barcode_base64}"
        except Exception as e:
            return ""
    
    def generate_qr_code(self):
        """Generate QR code image as base64 string"""
        try:
            # Create QR code with product information
            qr_data = {
                'id': str(self.id),
                'name': self.name,
                'sku': self.sku,
                'barcode': self.barcode,
                'price': str(self.price),
                'is_halal': self.is_halal
            }
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(str(qr_data))
            qr.make(fit=True)
            
            # Create image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Save to BytesIO
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            
            # Convert to base64
            buffer.seek(0)
            qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/png;base64,{qr_base64}"
        except Exception as e:
            return ""
    
    @property
    def is_expired(self):
        """Check if product is expired"""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False
    
    @property
    def is_expiring_soon(self):
        """Check if product is expiring within 30 days"""
        if self.expiry_date:
            thirty_days_from_now = timezone.now().date() + timedelta(days=30)
            return self.expiry_date <= thirty_days_from_now and not self.is_expired
        return False
    
    @property
    def days_until_expiry(self):
        """Calculate days until expiry"""
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None
    
    @property
    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.current_stock <= self.minimum_stock
    
    @property
    def stock_status(self):
        """Get stock status"""
        if self.current_stock == 0:
            return "OUT_OF_STOCK"
        elif self.is_low_stock:
            return "LOW_STOCK"
        elif self.current_stock >= self.maximum_stock:
            return "OVERSTOCK"
        else:
            return "NORMAL"


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUSTMENT', 'Stock Adjustment'),
        ('EXPIRED', 'Expired Stock Removal'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    previous_stock = models.PositiveIntegerField()
    new_stock = models.PositiveIntegerField()
    reason = models.CharField(max_length=200, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.transaction_type} - {self.quantity}"


class ExpiryAlert(models.Model):
    ALERT_TYPES = [
        ('EXPIRING_SOON', 'Expiring Soon (30 days)'),
        ('EXPIRED', 'Expired'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'alert_type']
    
    def __str__(self):
        return f"{self.product.name} - {self.alert_type}"


class ProductTicket(models.Model):
    """Product ticket/label for printing"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ticket_data = models.JSONField()  # Contains all ticket information
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ticket for {self.product.name}"