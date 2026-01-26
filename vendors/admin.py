from django.contrib import admin
from .models import Vendor, PurchaseOrder, PurchaseOrderItem

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_id', 'name', 'contact_person', 'phone', 'email', 'is_active')
    list_filter = ('is_active', 'created_date')
    search_fields = ('name', 'vendor_id', 'email')
    ordering = ('name',)

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'vendor', 'order_date', 'expected_delivery', 'status', 'total_amount')
    list_filter = ('status', 'order_date')
    search_fields = ('po_number', 'vendor__name')
    ordering = ('-order_date',)

@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('po', 'product', 'quantity_ordered', 'unit_cost', 'received_quantity')
    search_fields = ('po__po_number', 'product__product_name')
