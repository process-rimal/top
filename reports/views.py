from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from sales.models import Sale, SaleItem
from inventory.models import Product, Inventory
from customers.models import Customer
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg
import json

@login_required
def sales_report(request):
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    sales = Sale.objects.all()
    if date_from:
        sales = sales.filter(sale_date__gte=date_from)
    if date_to:
        sales = sales.filter(sale_date__lte=date_to)
    
    total_sales = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    sale_count = sales.count()
    avg_sale = sales.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
    
    context = {
        'sales': sales,
        'total_sales': total_sales,
        'sale_count': sale_count,
        'avg_sale': avg_sale
    }
    return render(request, 'reports/sales_report.html', context)

@login_required
def inventory_report(request):
    products = Product.objects.all()
    inventory_data = []
    
    for product in products:
        inv = Inventory.objects.get(product=product)
        inventory_data.append({
            'product': product,
            'quantity': inv.quantity,
            'value': inv.quantity * product.cost_price
        })
    
    total_value = sum(item['value'] for item in inventory_data)
    
    context = {
        'inventory': inventory_data,
        'total_value': total_value
    }
    return render(request, 'reports/inventory_report.html', context)

@login_required
def profit_loss_report(request):
    sales = Sale.objects.all()
    
    total_revenue = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    sale_items = SaleItem.objects.all()
    total_cost = sum(item.quantity * item.product.cost_price for item in sale_items)
    
    profit = total_revenue - total_cost
    
    context = {
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'profit': profit,
        'profit_margin': (profit / total_revenue * 100) if total_revenue > 0 else 0
    }
    return render(request, 'reports/profit_loss.html', context)

@login_required
def top_products_report(request):
    top_products = SaleItem.objects.values('product__product_name').annotate(
        total_qty=Sum('quantity'),
        total_sales=Sum('quantity')
    ).order_by('-total_qty')[:10]
    
    context = {'top_products': top_products}
    return render(request, 'reports/top_products.html', context)

@login_required
def customer_purchase_report(request):
    customers = Customer.objects.all()
    customer_data = []
    
    for customer in customers:
        sales = Sale.objects.filter(customer=customer)
        total_purchases = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        customer_data.append({
            'customer': customer,
            'purchases': sales.count(),
            'total_amount': total_purchases
        })
    
    context = {'customers': customer_data}
    return render(request, 'reports/customer_purchase.html', context)

@login_required
def daily_sales_trend(request):
    last_30_days = timezone.now().date() - timedelta(days=30)
    sales = Sale.objects.filter(sale_date__date__gte=last_30_days)
    
    daily_sales = {}
    for sale in sales:
        date = sale.sale_date.date()
        if date not in daily_sales:
            daily_sales[date] = 0
        daily_sales[date] += sale.total_amount
    
    context = {
        'daily_sales': json.dumps(daily_sales, default=str),
        'chart_data': [(date, amount) for date, amount in sorted(daily_sales.items())]
    }
    return render(request, 'reports/daily_trend.html', context)

@login_required
def dashboard_report(request):
    today = timezone.now().date()
    
    today_sales = Sale.objects.filter(sale_date__date=today)
    today_total = today_sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    
    low_stock = Inventory.objects.filter(quantity__lt=10).count()
    
    context = {
        'today_sales': today_total,
        'sales_count': today_sales.count(),
        'total_customers': total_customers,
        'total_products': total_products,
        'low_stock_count': low_stock
    }
    return render(request, 'reports/dashboard.html', context)
