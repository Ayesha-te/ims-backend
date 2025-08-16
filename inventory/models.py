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
import pandas as pd
import json


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
    
    # Link to supermarket or substore (one of them must be set)
    supermarket = models.ForeignKey('Supermarket', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    substore = models.ForeignKey('Substore', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    
    # Halal Verification
    is_halal = models.BooleanField(default=False)
    halal_certification_number = models.CharField(max_length=100, blank=True)
    halal_verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_products')
    halal_verified_date = models.DateTimeField(null=True, blank=True)
    
    # Product Details
    sku = models.CharField(max_length=50)
    barcode = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional Product Information
    brand = models.CharField(max_length=100, blank=True)
    weight = models.CharField(max_length=50, blank=True)
    origin = models.CharField(max_length=100, blank=True)
    product_image = models.TextField(blank=True)  # Base64 encoded product image
    
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
    
    # Import Information
    imported_from_excel = models.BooleanField(default=False)
    imported_from_image = models.BooleanField(default=False)
    import_batch_id = models.CharField(max_length=100, blank=True)  # For tracking bulk imports
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.substore:
            return f"{self.name} ({self.substore.supermarket.name} - {self.substore.name})"
        elif self.supermarket:
            return f"{self.name} ({self.supermarket.name})"
        return self.name
    
    @property
    def store_location(self):
        """Get the store location (supermarket or substore)"""
        if self.substore:
            return f"{self.substore.supermarket.name} - {self.substore.name}"
        elif self.supermarket:
            return self.supermarket.name
        return "Unknown"
    
    @property
    def parent_supermarket(self):
        """Get the parent supermarket regardless of whether product is in main store or substore"""
        if self.substore:
            return self.substore.supermarket
        return self.supermarket
    
    def save(self, *args, **kwargs):
        # Generate unique barcode if not exists
        if not self.barcode:
            if self.substore:
                self.barcode = f"HALAL{self.substore.supermarket.id}_{self.substore.id}_{self.sku}"
            elif self.supermarket:
                self.barcode = f"HALAL{self.supermarket.id}_{self.sku}"
            else:
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
                'is_halal': self.is_halal,
                'store_location': self.store_location,
                'supermarket': self.parent_supermarket.name if self.parent_supermarket else 'N/A',
                'substore': self.substore.name if self.substore else None
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


class Supermarket(models.Model):
    """Supermarket model for multi-vendor system"""
    # Link to Django User for authentication
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Business Information
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    description = models.TextField(blank=True)
    logo = models.URLField(blank=True)
    
    # Registration and Verification
    registration_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_supermarkets')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-registration_date']
    
    def __str__(self):
        return self.name
    
    @property
    def total_products(self):
        """Get total number of products for this supermarket including substores"""
        total = self.products.filter(is_active=True).count()
        for substore in self.substores.filter(is_active=True):
            total += substore.products.filter(is_active=True).count()
        return total
    
    @property
    def total_stock_value(self):
        """Calculate total stock value for this supermarket including substores"""
        from django.db.models import Sum, F
        total = self.products.filter(is_active=True).aggregate(
            total=Sum(F('current_stock') * F('cost_price'))
        )['total'] or 0
        
        for substore in self.substores.filter(is_active=True):
            substore_total = substore.products.filter(is_active=True).aggregate(
                total=Sum(F('current_stock') * F('cost_price'))
            )['total'] or 0
            total += substore_total
        
        return total


class Substore(models.Model):
    """Substore model for managing multiple locations under one supermarket"""
    # Link to parent supermarket
    supermarket = models.ForeignKey(Supermarket, on_delete=models.CASCADE, related_name='substores')
    
    # Substore Information
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    description = models.TextField(blank=True)
    
    # Manager Information (optional separate user for substore management)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_substores')
    
    # Registration and Status
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_date']
        unique_together = ['supermarket', 'name']  # Unique substore name per supermarket
    
    def __str__(self):
        return f"{self.supermarket.name} - {self.name}"
    
    @property
    def total_products(self):
        """Get total number of products for this substore"""
        return self.products.filter(is_active=True).count()
    
    @property
    def total_stock_value(self):
        """Calculate total stock value for this substore"""
        from django.db.models import Sum, F
        return self.products.filter(is_active=True).aggregate(
            total=Sum(F('current_stock') * F('cost_price'))
        )['total'] or 0


class ExcelImport(models.Model):
    """Model to track Excel file imports"""
    IMPORT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    # Import Information
    batch_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    file_name = models.CharField(max_length=255)
    file_data = models.TextField()  # Base64 encoded Excel file
    
    # User and Store Information
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    supermarket = models.ForeignKey(Supermarket, on_delete=models.CASCADE, null=True, blank=True)
    substore = models.ForeignKey(Substore, on_delete=models.CASCADE, null=True, blank=True)
    
    # Processing Information
    status = models.CharField(max_length=20, choices=IMPORT_STATUS_CHOICES, default='PENDING')
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    successful_imports = models.PositiveIntegerField(default=0)
    failed_imports = models.PositiveIntegerField(default=0)
    error_log = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Excel Import: {self.file_name} ({self.status})"
    
    @classmethod
    def process_excel_file(cls, excel_import_instance):
        """Process Excel file and create products"""
        import pandas as pd
        import base64
        from io import BytesIO
        
        try:
            excel_import_instance.status = 'PROCESSING'
            excel_import_instance.started_at = timezone.now()
            excel_import_instance.save()
            
            # Decode base64 file data
            file_data = base64.b64decode(excel_import_instance.file_data)
            excel_file = BytesIO(file_data)
            
            # Read Excel file
            df = pd.read_excel(excel_file)
            excel_import_instance.total_rows = len(df)
            excel_import_instance.save()
            
            errors = []
            successful_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Extract product data from Excel row
                    product_data = cls._extract_product_data_from_row(row, excel_import_instance)
                    
                    # Create product
                    product = Product.objects.create(**product_data)
                    successful_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")
                
                excel_import_instance.processed_rows = index + 1
                excel_import_instance.save()
            
            # Update final status
            excel_import_instance.successful_imports = successful_count
            excel_import_instance.failed_imports = len(errors)
            excel_import_instance.error_log = '\n'.join(errors)
            excel_import_instance.status = 'COMPLETED'
            excel_import_instance.completed_at = timezone.now()
            excel_import_instance.save()
            
        except Exception as e:
            excel_import_instance.status = 'FAILED'
            excel_import_instance.error_log = str(e)
            excel_import_instance.completed_at = timezone.now()
            excel_import_instance.save()
    
    @staticmethod
    def _extract_product_data_from_row(row, excel_import_instance):
        """Extract product data from Excel row"""
        # Get or create category
        category_name = row.get('category', 'Other')
        category, _ = Category.objects.get_or_create(name=category_name)
        
        # Get or create supplier
        supplier_name = row.get('supplier', 'Unknown')
        supplier, _ = Supplier.objects.get_or_create(
            name=supplier_name,
            defaults={'halal_certified': True}
        )
        
        return {
            'name': row.get('name', ''),
            'description': row.get('description', ''),
            'category': category,
            'supplier': supplier,
            'supermarket': excel_import_instance.supermarket,
            'substore': excel_import_instance.substore,
            'sku': row.get('sku', ''),
            'price': float(row.get('price', 0)),
            'cost_price': float(row.get('cost_price', row.get('price', 0))),
            'current_stock': int(row.get('current_stock', 0)),
            'minimum_stock': int(row.get('minimum_stock', 10)),
            'maximum_stock': int(row.get('maximum_stock', 1000)),
            'brand': row.get('brand', ''),
            'weight': row.get('weight', ''),
            'origin': row.get('origin', ''),
            'manufacturing_date': pd.to_datetime(row.get('manufacturing_date')).date() if pd.notna(row.get('manufacturing_date')) else None,
            'expiry_date': pd.to_datetime(row.get('expiry_date')).date() if pd.notna(row.get('expiry_date')) else None,
            'is_halal': bool(row.get('is_halal', True)),
            'halal_certification_number': row.get('halal_certification_number', ''),
            'imported_from_excel': True,
            'import_batch_id': str(excel_import_instance.batch_id),
        }


class ImageImport(models.Model):
    """Model to track image-based product imports"""
    IMPORT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    # Import Information
    batch_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    image_name = models.CharField(max_length=255)
    image_data = models.TextField()  # Base64 encoded image
    
    # User and Store Information
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    supermarket = models.ForeignKey(Supermarket, on_delete=models.CASCADE, null=True, blank=True)
    substore = models.ForeignKey(Substore, on_delete=models.CASCADE, null=True, blank=True)
    
    # Processing Information
    status = models.CharField(max_length=20, choices=IMPORT_STATUS_CHOICES, default='PENDING')
    extracted_text = models.TextField(blank=True)
    extracted_data = models.JSONField(default=dict)
    error_log = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Image Import: {self.image_name} ({self.status})"
    
    @classmethod
    def process_image_file(cls, image_import_instance):
        """Process image file and extract product information"""
        try:
            image_import_instance.status = 'PROCESSING'
            image_import_instance.started_at = timezone.now()
            image_import_instance.save()
            
            # For now, we'll implement a basic text extraction
            # In a real implementation, you would use OCR libraries like pytesseract
            # or cloud services like Google Vision API, AWS Textract, etc.
            
            extracted_data = cls._extract_data_from_image(image_import_instance.image_data)
            
            image_import_instance.extracted_data = extracted_data
            image_import_instance.status = 'COMPLETED'
            image_import_instance.completed_at = timezone.now()
            image_import_instance.save()
            
            return extracted_data
            
        except Exception as e:
            image_import_instance.status = 'FAILED'
            image_import_instance.error_log = str(e)
            image_import_instance.completed_at = timezone.now()
            image_import_instance.save()
            return {}
    
    @staticmethod
    def _extract_data_from_image(image_data):
        """Extract product data from image using OCR"""
        try:
            import pytesseract
            import cv2
            import numpy as np
            from PIL import Image as PILImage
            import base64
            import re
            from io import BytesIO
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
            image = PILImage.open(BytesIO(image_bytes))
            
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get better text recognition
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Extract text using pytesseract
            extracted_text = pytesseract.image_to_string(thresh, config='--psm 6')
            
            # Parse extracted text to find product information
            lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
            
            # Initialize extracted data
            extracted_data = {
                'name': '',
                'price': '',
                'description': '',
                'brand': '',
                'weight': '',
                'expiry_date': '',
                'barcode': '',
                'extracted_text': extracted_text
            }
            
            # Try to extract specific information using patterns
            for line in lines:
                # Price patterns
                price_match = re.search(r'[\$£€¥₹]?\s*(\d+\.?\d*)', line.lower())
                if price_match and not extracted_data['price']:
                    extracted_data['price'] = price_match.group(1)
                
                # Weight/size patterns
                weight_match = re.search(r'(\d+\.?\d*\s*(kg|g|lb|oz|ml|l|litre|liter))', line.lower())
                if weight_match and not extracted_data['weight']:
                    extracted_data['weight'] = weight_match.group(1)
                
                # Date patterns (for expiry)
                date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', line)
                if date_match and ('exp' in line.lower() or 'best' in line.lower()):
                    extracted_data['expiry_date'] = date_match.group(1)
                
                # Barcode patterns
                barcode_match = re.search(r'(\d{8,14})', line)
                if barcode_match and len(barcode_match.group(1)) >= 8:
                    extracted_data['barcode'] = barcode_match.group(1)
            
            # Use first few lines as potential product name
            if lines and not extracted_data['name']:
                # Filter out lines that look like prices, dates, or barcodes
                potential_names = []
                for line in lines[:5]:  # Check first 5 lines
                    if not re.search(r'[\$£€¥₹]\s*\d+', line) and not re.search(r'\d{8,}', line):
                        potential_names.append(line)
                
                if potential_names:
                    extracted_data['name'] = potential_names[0]
            
            # Use remaining text as description
            if len(lines) > 1:
                extracted_data['description'] = ' '.join(lines[1:3])  # Use next 2 lines
            
            return extracted_data
            
        except Exception as e:
            # Fallback to basic extraction
            return {
                'name': 'Product extracted from image',
                'price': '0.00',
                'description': 'Product information extracted from uploaded image',
                'error': str(e),
                'note': 'OCR processing failed, using fallback data.'
            }


