from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Supplier, Product, StockTransaction, ExpiryAlert, ProductTicket


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'halal_certified', 'created_at']
    list_filter = ['halal_certified', 'created_at']
    search_fields = ['name', 'contact_person', 'phone', 'email']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_person', 'phone', 'email', 'address')
        }),
        ('Halal Certification', {
            'fields': ('halal_certified', 'certification_number')
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'supplier', 'is_halal', 
        'current_stock', 'stock_status_display', 'expiry_status_display', 
        'price', 'is_active'
    ]
    list_filter = [
        'is_halal', 'category', 'supplier', 'is_active', 
        'created_at', 'expiry_date'
    ]
    search_fields = ['name', 'sku', 'barcode', 'description']
    readonly_fields = [
        'id', 'barcode', 'barcode_image', 'qr_code_image', 
        'created_at', 'updated_at', 'stock_status_display',
        'expiry_status_display', 'is_expired', 'is_expiring_soon',
        'days_until_expiry'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'supplier', 'sku')
        }),
        ('Halal Verification', {
            'fields': (
                'is_halal', 'halal_certification_number', 
                'halal_verified_by', 'halal_verified_date'
            )
        }),
        ('Product Details', {
            'fields': ('price', 'cost_price', 'barcode')
        }),
        ('Stock Information', {
            'fields': (
                'current_stock', 'minimum_stock', 'maximum_stock',
                'stock_status_display'
            )
        }),
        ('Dates', {
            'fields': (
                'manufacturing_date', 'expiry_date', 'expiry_status_display',
                'days_until_expiry'
            )
        }),
        ('Generated Assets', {
            'fields': ('barcode_image', 'qr_code_image'),
            'classes': ('collapse',)
        }),
        ('System Fields', {
            'fields': ('id', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status_display(self, obj):
        status = obj.stock_status
        colors = {
            'OUT_OF_STOCK': 'red',
            'LOW_STOCK': 'orange',
            'NORMAL': 'green',
            'OVERSTOCK': 'blue'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(status, 'black'),
            status.replace('_', ' ')
        )
    stock_status_display.short_description = 'Stock Status'
    
    def expiry_status_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red; font-weight: bold;">EXPIRED</span>')
        elif obj.is_expiring_soon:
            return format_html('<span style="color: orange; font-weight: bold;">EXPIRING SOON</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">GOOD</span>')
    expiry_status_display.short_description = 'Expiry Status'
    
    def get_queryset(self, request):
        # Show only Halal products by default
        return super().get_queryset(request).filter(is_halal=True)


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'transaction_type', 'quantity', 'previous_stock',
        'new_stock', 'user', 'created_at'
    ]
    list_filter = ['transaction_type', 'created_at', 'user']
    search_fields = ['product__name', 'product__sku', 'reason']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'product', 'transaction_type', 'quantity', 
                'previous_stock', 'new_stock', 'reason'
            )
        }),
        ('System Fields', {
            'fields': ('user', 'created_at')
        }),
    )


@admin.register(ExpiryAlert)
class ExpiryAlertAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'alert_type', 'product_expiry_date', 
        'days_until_expiry', 'is_read', 'created_at'
    ]
    list_filter = ['alert_type', 'is_read', 'created_at']
    search_fields = ['product__name', 'product__sku']
    readonly_fields = ['created_at', 'product_expiry_date', 'days_until_expiry']
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def product_expiry_date(self, obj):
        return obj.product.expiry_date
    product_expiry_date.short_description = 'Expiry Date'
    
    def days_until_expiry(self, obj):
        return obj.product.days_until_expiry
    days_until_expiry.short_description = 'Days Until Expiry'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} alerts marked as read.')
    mark_as_read.short_description = 'Mark selected alerts as read'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} alerts marked as unread.')
    mark_as_unread.short_description = 'Mark selected alerts as unread'


@admin.register(ProductTicket)
class ProductTicketAdmin(admin.ModelAdmin):
    list_display = ['product', 'created_by', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['product__name', 'product__sku']
    readonly_fields = ['ticket_data', 'created_at']
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('product', 'created_by')
        }),
        ('Ticket Data', {
            'fields': ('ticket_data',),
            'classes': ('collapse',)
        }),
        ('System Fields', {
            'fields': ('created_at',)
        }),
    )