from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from inventory.models import Category, Supplier, Product
import random


class Command(BaseCommand):
    help = 'Set up initial inventory data with sample Halal products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-sample-data',
            action='store_true',
            help='Create sample products and data',
        )
        parser.add_argument(
            '--admin-user',
            type=str,
            help='Admin username to create',
            default='admin'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up Halal Inventory Management System...')
        )

        # Create admin user if it doesn't exist
        admin_username = options['admin_user']
        admin_user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                'email': 'admin@halalinventory.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Admin user "{admin_username}" created with password "admin123"')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Admin user "{admin_username}" already exists')
            )

        # Create basic categories
        categories_data = [
            {'name': 'Meat & Poultry', 'description': 'Halal certified meat and poultry products'},
            {'name': 'Dairy Products', 'description': 'Halal certified dairy and milk products'},
            {'name': 'Packaged Foods', 'description': 'Halal certified packaged and processed foods'},
            {'name': 'Beverages', 'description': 'Halal certified drinks and beverages'},
            {'name': 'Snacks & Confectionery', 'description': 'Halal certified snacks, sweets and confectionery'},
            {'name': 'Frozen Foods', 'description': 'Halal certified frozen food products'},
            {'name': 'Bakery Items', 'description': 'Halal certified bakery and bread products'},
            {'name': 'Spices & Condiments', 'description': 'Halal certified spices and cooking ingredients'},
        ]

        categories_created = 0
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                categories_created += 1

        self.stdout.write(
            self.style.SUCCESS(f'✅ Created {categories_created} categories')
        )

        # Create suppliers
        suppliers_data = [
            {
                'name': 'Al-Halal Meat Suppliers',
                'contact_person': 'Ahmed Hassan',
                'phone': '+1-555-0101',
                'email': 'ahmed@alhalalmet.com',
                'address': '123 Halal Street, Islamic District',
                'halal_certified': True,
                'certification_number': 'HCS-2024-001'
            },
            {
                'name': 'Crescent Foods Distribution',
                'contact_person': 'Fatima Ali',
                'phone': '+1-555-0102',
                'email': 'fatima@crescentfoods.com',
                'address': '456 Moon Avenue, Muslim Quarter',
                'halal_certified': True,
                'certification_number': 'HCS-2024-002'
            },
            {
                'name': 'Islamic Grocers Ltd',
                'contact_person': 'Omar Khan',
                'phone': '+1-555-0103',
                'email': 'omar@islamicgrocers.com',
                'address': '789 Faith Road, Community Center',
                'halal_certified': True,
                'certification_number': 'HCS-2024-003'
            },
            {
                'name': 'Salam International Foods',
                'contact_person': 'Aisha Rahman',
                'phone': '+1-555-0104',
                'email': 'aisha@salamfoods.com',
                'address': '321 Peace Boulevard, Trading District',
                'halal_certified': True,
                'certification_number': 'HCS-2024-004'
            },
        ]

        suppliers_created = 0
        for sup_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=sup_data['name'],
                defaults=sup_data
            )
            if created:
                suppliers_created += 1

        self.stdout.write(
            self.style.SUCCESS(f'✅ Created {suppliers_created} Halal certified suppliers')
        )

        if options['with_sample_data']:
            self.create_sample_products(admin_user)

        self.stdout.write(
            self.style.SUCCESS('🎉 Halal Inventory Management System setup completed!')
        )
        self.stdout.write('📋 Summary:')
        self.stdout.write(f'   • Categories: {Category.objects.count()}')
        self.stdout.write(f'   • Suppliers: {Supplier.objects.count()}')
        self.stdout.write(f'   • Products: {Product.objects.count()}')
        self.stdout.write('')
        self.stdout.write('🌐 Access your system at:')
        self.stdout.write('   • Admin: http://localhost:8000/admin/')
        self.stdout.write('   • API: http://localhost:8000/api/')

    def create_sample_products(self, admin_user):
        """Create sample Halal products"""
        self.stdout.write('📦 Creating sample Halal products...')
        
        categories = Category.objects.all()
        suppliers = Supplier.objects.all()
        
        if not categories.exists() or not suppliers.exists():
            self.stdout.write(
                self.style.ERROR('❌ Please create categories and suppliers first')
            )
            return

        sample_products = [
            # Meat & Poultry
            {
                'name': 'Halal Chicken Breast (1kg)',
                'category': 'Meat & Poultry',
                'description': 'Fresh Halal certified chicken breast, locally sourced',
                'price': Decimal('15.99'),
                'cost_price': Decimal('12.50'),
                'current_stock': 50,
                'minimum_stock': 10,
                'expiry_days': 5
            },
            {
                'name': 'Halal Ground Beef (500g)',
                'category': 'Meat & Poultry',
                'description': 'Premium Halal ground beef, 85% lean',
                'price': Decimal('12.99'),
                'cost_price': Decimal('10.00'),
                'current_stock': 30,
                'minimum_stock': 5,
                'expiry_days': 7
            },
            {
                'name': 'Halal Lamb Chops (1kg)',
                'category': 'Meat & Poultry',
                'description': 'Tender Halal lamb chops, premium cut',
                'price': Decimal('28.99'),
                'cost_price': Decimal('22.00'),
                'current_stock': 20,
                'minimum_stock': 5,
                'expiry_days': 10
            },

            # Dairy Products
            {
                'name': 'Halal Cheddar Cheese (250g)',
                'category': 'Dairy Products',
                'description': 'Aged Halal cheddar cheese, smooth texture',
                'price': Decimal('8.99'),
                'cost_price': Decimal('6.50'),
                'current_stock': 40,
                'minimum_stock': 15,
                'expiry_days': 45
            },
            {
                'name': 'Halal Milk (1L)',
                'category': 'Dairy Products',
                'description': 'Fresh Halal certified whole milk',
                'price': Decimal('3.99'),
                'cost_price': Decimal('2.80'),
                'current_stock': 60,
                'minimum_stock': 20,
                'expiry_days': 7
            },

            # Packaged Foods
            {
                'name': 'Halal Pasta Sauce (500ml)',
                'category': 'Packaged Foods',
                'description': 'Organic Halal tomato-based pasta sauce',
                'price': Decimal('4.99'),
                'cost_price': Decimal('3.20'),
                'current_stock': 35,
                'minimum_stock': 10,
                'expiry_days': 180
            },
            {
                'name': 'Halal Instant Noodles Pack',
                'category': 'Packaged Foods',
                'description': 'Quick Halal instant noodles with seasoning',
                'price': Decimal('2.99'),
                'cost_price': Decimal('1.80'),
                'current_stock': 80,
                'minimum_stock': 25,
                'expiry_days': 365
            },

            # Products expiring soon (for testing alerts)
            {
                'name': 'Halal Yogurt (200g) - Expiring Soon',
                'category': 'Dairy Products',
                'description': 'Natural Halal yogurt - Special clearance',
                'price': Decimal('2.50'),
                'cost_price': Decimal('1.80'),
                'current_stock': 15,
                'minimum_stock': 5,
                'expiry_days': 25  # Will trigger expiring soon alert
            },
            {
                'name': 'Halal Bread Loaf - Close to Expiry',
                'category': 'Bakery Items',
                'description': 'Fresh Halal white bread - Quick sale',
                'price': Decimal('1.99'),
                'cost_price': Decimal('1.20'),
                'current_stock': 8,
                'minimum_stock': 10,  # Will trigger low stock alert
                'expiry_days': 2  # Will trigger expired alert soon
            },

            # Beverages
            {
                'name': 'Halal Apple Juice (1L)',
                'category': 'Beverages',
                'description': '100% pure Halal apple juice, no additives',
                'price': Decimal('5.99'),
                'cost_price': Decimal('4.20'),
                'current_stock': 25,
                'minimum_stock': 10,
                'expiry_days': 90
            },

            # Snacks
            {
                'name': 'Halal Mixed Nuts (300g)',
                'category': 'Snacks & Confectionery',
                'description': 'Premium Halal mixed nuts and dried fruits',
                'price': Decimal('9.99'),
                'cost_price': Decimal('7.50'),
                'current_stock': 45,
                'minimum_stock': 15,
                'expiry_days': 120
            },
        ]

        products_created = 0
        for product_data in sample_products:
            try:
                category = categories.get(name=product_data['category'])
                supplier = suppliers.first()  # Use first supplier
                
                # Generate unique SKU
                sku = f"HAL-{category.name[:3].upper()}-{products_created + 1:04d}"
                
                # Calculate dates
                today = timezone.now().date()
                manufacturing_date = today - timedelta(days=random.randint(1, 30))
                expiry_date = today + timedelta(days=product_data['expiry_days'])
                
                product, created = Product.objects.get_or_create(
                    sku=sku,
                    defaults={
                        'name': product_data['name'],
                        'description': product_data['description'],
                        'category': category,
                        'supplier': supplier,
                        'is_halal': True,  # All products are Halal
                        'halal_certification_number': f'HC-{sku}',
                        'halal_verified_by': admin_user,
                        'halal_verified_date': timezone.now(),
                        'price': product_data['price'],
                        'cost_price': product_data['cost_price'],
                        'current_stock': product_data['current_stock'],
                        'minimum_stock': product_data['minimum_stock'],
                        'maximum_stock': product_data['current_stock'] * 3,
                        'manufacturing_date': manufacturing_date,
                        'expiry_date': expiry_date,
                        'is_active': True,
                    }
                )
                
                if created:
                    products_created += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error creating product "{product_data["name"]}": {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'✅ Created {products_created} sample Halal products')
        )