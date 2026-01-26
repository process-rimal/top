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
