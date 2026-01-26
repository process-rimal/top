from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from .models import Sale, SaleItem
from inventory.models import Product, Inventory
from customers.models import Customer
from .utils import generate_receipt_pdf
import json

@login_required
def pos_view(request):
    context = {
        'products': Product.objects.all(),
        'customers': Customer.objects.all(),
    }
    return render(request, 'sales/pos.html', context)

@login_required
@require_http_methods(["GET"])
def search_product_api(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'products': []})
    
    products = Product.objects.filter(
        Q(product_name__icontains=query) |
        Q(barcode__icontains=query) |
        Q(sku__icontains=query)
    )[:10]
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.product_name,
            'sku': product.sku,
            'barcode': product.barcode,
            'price': str(product.selling_price),
            'stock': product.current_stock,
        })
    
    return JsonResponse({'products': results})

@login_required
@require_http_methods(["GET"])
def get_customer_api(request):
    phone = request.GET.get('phone', '')
    try:
        customer = Customer.objects.get(phone_number=phone)
        return JsonResponse({
            'found': True,
            'name': customer.customer_name,
            'phone': customer.phone_number,
            'credit_limit': str(customer.total_credit_limit),
            'current_credit': str(customer.current_credit),
            'available_credit': str(customer.available_credit),
        })
    except Customer.DoesNotExist:
        return JsonResponse({'found': False})

@login_required
@require_http_methods(["POST"])
@transaction.atomic
def create_sale_api(request):
    try:
        data = json.loads(request.body)
        
        customer = None
        if data.get('customer_phone'):
            customer, _ = Customer.objects.get_or_create(
                phone_number=data['customer_phone'],
                defaults={'customer_name': data.get('customer_name', 'Walk-in Customer')}
            )
        
        payment_method = data.get('payment_method', 'cash')
        paid_amount = float(data.get('paid_amount', 0))
        total_amount = float(data['total'])

        sale = Sale.objects.create(
            customer=customer,
            cashier=request.user.profile,
            subtotal=float(data['subtotal']),
            discount=float(data.get('discount', 0)),
            discount_percent=float(data.get('discount_percent', 0)),
            tax=float(data['tax']),
            total_amount=total_amount,
            payment_method=payment_method,
            payment_status='paid' if paid_amount >= total_amount else 'partial',
            paid_amount=paid_amount,
        )
        
        for item in data['items']:
            product = Product.objects.get(id=int(item['product_id']))
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=int(item['quantity']),
                unit_price=float(item['price']),
                discount_percent=float(item.get('discount', 0)),
                line_total=float(item['line_total']),
            )
            
            inventory, _ = Inventory.objects.get_or_create(product=product, defaults={'quantity_in_stock': 0})
            inventory.quantity_in_stock -= int(item['quantity'])
            inventory.save()
        
        if customer and payment_method == 'credit':
            from customers.models import CreditTransaction
            customer.current_credit += total_amount
            customer.save()
            CreditTransaction.objects.create(
                customer=customer,
                transaction_type='purchase',
                amount=total_amount,
                balance_after=customer.current_credit,
                related_sale=sale,
            )
        
        return JsonResponse({
            'success': True,
            'sale_number': sale.sale_number,
            'receipt_number': sale.receipt_number,
            'message': 'Sale created successfully'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def print_receipt(request, sale_number):
    sale = get_object_or_404(Sale, sale_number=sale_number)
    return render(request, 'sales/receipt.html', {'sale': sale})

@login_required
def receipt_pdf(request, sale_number):
    sale = get_object_or_404(Sale, sale_number=sale_number)
    buffer = generate_receipt_pdf(sale)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{sale_number}.pdf"'
    return response

@login_required
def sales_list(request):
    sales = Sale.objects.all().order_by('-sale_date')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    if from_date:
        sales = sales.filter(sale_date__date__gte=from_date)
    if to_date:
        sales = sales.filter(sale_date__date__lte=to_date)
    
    return render(request, 'sales/sales_list.html', {'sales': sales})

@login_required
def sales_detail(request, sale_number):
    sale = get_object_or_404(Sale, sale_number=sale_number)
    return render(request, 'sales/sales_detail.html', {'sale': sale})
