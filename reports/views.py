from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum, Count, Avg
from sales.models import Sale
from inventory.models import Product, Inventory
from customers.models import Customer
from vendors.models import Vendor

@login_required
def reports_dashboard(request):
    return render(request, 'reports/dashboard.html')

@login_required
def sales_report(request):
    sales = Sale.objects.all()
    total_sales = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    sale_count = sales.count()
    return render(request, 'reports/sales_report.html', {
        'sales': sales,
        'total_sales': total_sales,
        'sale_count': sale_count
    })

@login_required
def inventory_report(request):
    products = Product.objects.all()
    return render(request, 'reports/inventory_report.html', {'products': products})

@login_required
def customer_report(request):
    customers = Customer.objects.all()
    return render(request, 'reports/customer_report.html', {'customers': customers})

@login_required
def vendor_report(request):
    vendors = Vendor.objects.all()
    return render(request, 'reports/vendor_report.html', {'vendors': vendors})

@login_required
def export_sales(request):
    return HttpResponse("Export sales - Coming soon", content_type='text/plain')

@login_required
def export_inventory(request):
    return HttpResponse("Export inventory - Coming soon", content_type='text/plain')
