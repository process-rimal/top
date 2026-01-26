from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Sale, SaleItem
from inventory.models import Product, Inventory
from customers.models import Customer
from datetime import datetime, timedelta
import json

@login_required
def pos_system(request):
    products = Product.objects.all()
    customers = Customer.objects.all()
    context = {
        'products': products,
        'customers': customers
    }
    return render(request, 'sales/pos.html', context)

@login_required
def create_sale(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        items = data.get('items')
        payment_method = data.get('payment_method')
        
        customer = Customer.objects.get(id=customer_id) if customer_id else None
        
        sale = Sale.objects.create(
            salesperson=request.user,
            customer=customer,
            sale_date=timezone.now(),
            payment_method=payment_method
        )
        
        total_amount = 0
        for item in items:
            product = Product.objects.get(id=item['product_id'])
            quantity = int(item['quantity'])
            price = float(item['price'])
            
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                price=price
            )
            
            # Update inventory
            inventory = Inventory.objects.get(product=product)
            inventory.quantity -= quantity
            inventory.save()
            
            total_amount += quantity * price
        
        sale.total_amount = total_amount
        sale.save()
        
        return JsonResponse({'sale_id': sale.id, 'total': total_amount})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def sale_list(request):
    sales = Sale.objects.all().order_by('-sale_date')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        sales = sales.filter(sale_date__gte=date_from)
    if date_to:
        sales = sales.filter(sale_date__lte=date_to)
    
    context = {'sales': sales}
    return render(request, 'sales/sale_list.html', context)

@login_required
def sale_detail(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    items = SaleItem.objects.filter(sale=sale)
    context = {
        'sale': sale,
        'items': items
    }
    return render(request, 'sales/sale_detail.html', context)

@login_required
def generate_receipt(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    items = SaleItem.objects.filter(sale=sale)
    context = {
        'sale': sale,
        'items': items
    }
    return render(request, 'sales/receipt.html', context)

@login_required
def daily_sales(request):
    today = timezone.now().date()
    sales = Sale.objects.filter(sale_date__date=today)
    total_sales = sum(sale.total_amount for sale in sales)
    
    context = {
        'sales': sales,
        'total_sales': total_sales,
        'count': sales.count()
    }
    return render(request, 'sales/daily_sales.html', context)

@login_required
def sales_by_date(request):
    if request.method == 'GET':
        date_str = request.GET.get('date')
        if date_str:
            sale_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            sales = Sale.objects.filter(sale_date__date=sale_date)
            total = sum(sale.total_amount for sale in sales)
            return JsonResponse({
                'count': sales.count(),
                'total': float(total)
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
