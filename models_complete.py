# accounts/models.py - User Authentication Models

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class UserProfile(models.Model):
    """Extended user profile with shop-specific information"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Shop Staff'),
        ('manager', 'Manager'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_profile'
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"


# ========================================
# inventory/models.py - Product & Stock Models

from django.db import models

class Category(models.Model):
    """Product Categories"""
    
    CATEGORY_TYPE = [
        ('stationery', 'Stationery'),
        ('books', 'Books'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPE)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        ordering = ['name']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Product Master Data"""
    
    sku = models.CharField(max_length=50, unique=True)  # Stock Keeping Unit
    barcode = models.CharField(max_length=100, unique=True, blank=True)
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True)
    
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)  # Purchase price
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)  # Retail price
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    reorder_level = models.IntegerField(default=10)  # Alert when stock falls below this
    unit = models.CharField(max_length=20, default='piece')
    
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['product_name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
        ]
    
    def __str__(self):
        return self.product_name
    
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0
    
    @property
    def current_stock(self):
        """Get current stock quantity"""
        try:
            return self.inventory.quantity_in_stock
        except:
            return 0


class Inventory(models.Model):
    """Stock Management"""
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity_in_stock = models.IntegerField(default=0)
    quantity_reserved = models.IntegerField(default=0)  # Reserved for pending orders
    last_restock_date = models.DateField(null=True, blank=True)
    last_counted_date = models.DateField(null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory'
        verbose_name_plural = 'Inventory'
    
    def __str__(self):
        return f"{self.product.product_name} - {self.quantity_in_stock} units"
    
    @property
    def available_stock(self):
        """Available stock = Total - Reserved"""
        return self.quantity_in_stock - self.quantity_reserved
    
    @property
    def low_stock_alert(self):
        """Check if stock is low"""
        return self.quantity_in_stock <= self.product.reorder_level


class StockAdjustment(models.Model):
    """Track stock adjustments"""
    
    ADJUSTMENT_TYPE = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Stock Adjustment'),
        ('damage', 'Damage/Loss'),
        ('return', 'Customer Return'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPE)
    quantity_adjusted = models.IntegerField()
    notes = models.TextField(blank=True)
    adjusted_by = models.ForeignKey('accounts.UserProfile', on_delete=models.SET_NULL, null=True)
    adjusted_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_adjustments'
        ordering = ['-adjusted_date']
    
    def __str__(self):
        return f"{self.product.product_name} - {self.adjustment_type}"


# ========================================
# vendors/models.py - Vendor & Purchase Order Models

from django.db import models

class Vendor(models.Model):
    """Vendor/Supplier Information"""
    
    vendor_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=50)
    payment_terms = models.CharField(max_length=200, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vendors'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    """Purchase Orders to Vendors"""
    
    PO_STATUS = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
        ('partial', 'Partially Received'),
    ]
    
    po_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='purchase_orders')
    order_date = models.DateField(auto_now_add=True)
    expected_delivery = models.DateField()
    status = models.CharField(max_length=20, choices=PO_STATUS, default='pending')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_by = models.ForeignKey('accounts.UserProfile', on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchase_orders'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"PO-{self.po_number}"


class PurchaseOrderItem(models.Model):
    """Individual Items in a Purchase Order"""
    
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    quantity_ordered = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    received_quantity = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'purchase_order_items'
        unique_together = ['po', 'product']
    
    def __str__(self):
        return f"{self.product.product_name} - {self.quantity_ordered} units"
    
    def line_total(self):
        return self.quantity_ordered * self.unit_cost
    
    def received_total(self):
        return self.received_quantity * self.unit_cost


# ========================================
# customers/models.py - Customer & Credit Models

from django.db import models
from django.core.validators import RegexValidator

class Customer(models.Model):
    """Customer Database - Mobile number as primary identifier"""
    
    phone_regex = RegexValidator(
        regex=r'^\+?977?9\d{8,9}$',  # Nepal phone format
        message="Enter valid Nepal mobile number (+977 format)",
    )
    
    # Nepal format: +977XXXXXXXXXX or 9XXXXXXXXX
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[phone_regex],
        db_index=True
    )
    secondary_phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[phone_regex]
    )
    
    customer_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    
    # Credit Management
    current_credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loyalty_points = models.IntegerField(default=0)
    
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        ordering = ['customer_name']
        indexes = [
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return f"{self.customer_name} ({self.phone_number})"
    
    


class CreditTransaction(models.Model):
    """Credit Transaction History"""
    
    TRANSACTION_TYPE = [
        ('purchase', 'Purchase'),
        ('payment', 'Payment Received'),
        ('adjustment', 'Credit Adjustment'),
        ('refund', 'Refund'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='credit_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)  # Running balance
    
    description = models.TextField(blank=True)
    related_sale = models.ForeignKey('sales.Sale', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_by = models.ForeignKey('accounts.UserProfile', on_delete=models.SET_NULL, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'credit_transactions'
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.customer.customer_name} - {self.transaction_type}"


# ========================================
# sales/models.py - Sales & Billing Models

from django.db import models
from django.utils import timezone

class Sale(models.Model):
    """Sales/Billing Records"""
    
    PAYMENT_METHOD = [
        ('cash', 'Cash'),
        ('card', 'QR'),
        ('credit', 'Credit'),
        ('cheque', 'Cheque'),
        ('momo', 'Mobile Money'),
    ]
    
    PAYMENT_STATUS = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
    ]
    
    sale_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    
    cashier = models.ForeignKey('accounts.UserProfile', on_delete=models.SET_NULL, null=True)
    sale_date = models.DateTimeField(auto_now_add=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # VAT 13% (Nepal)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='cash')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='paid')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    is_printed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'sales'
        ordering = ['-sale_date']
        indexes = [
            models.Index(fields=['sale_number']),
            models.Index(fields=['sale_date']),
        ]
    
    def __str__(self):
        return f"Sale {self.sale_number}"
    
    def save(self, *args, **kwargs):
        # Auto-generate sale number
        if not self.sale_number:
            last_sale = Sale.objects.all().order_by('id').last()
            last_id = last_sale.id if last_sale else 0
            self.sale_number = f"SAL{timezone.now().strftime('%Y%m%d')}{last_id + 1:05d}"
        
        # Calculate due amount
        if self.paid_amount > 0:
            if self.paid_amount >= self.total_amount:
                self.payment_status = 'paid'
            else:
                self.payment_status = 'partial'
        
        super().save(*args, **kwargs)
    
    def due_amount(self):
        return self.total_amount - self.paid_amount


class SaleItem(models.Model):
    """Individual Items in a Sale"""
    
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('inventory.Product', on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        db_table = 'sale_items'
    
    def __str__(self):
        return f"{self.product.product_name} x {self.quantity}"
    
    def get_discount_amount(self):
        """Calculate discount amount for this line"""
        gross = self.unit_price * self.quantity
        return (gross * self.discount_percent) / 100
