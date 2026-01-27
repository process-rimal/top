from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from .models import Sale, SaleItem
from inventory.models import Product, Inventory
from customers.models import Customer
from .utils import generate_receipt_pdf, number_to_words
from decimal import Decimal
import json

@login_required
def sales_home(request):
    return render(request, 'sales/sales_home.html')


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
        customer = Customer.objects.get(
            Q(phone_number=phone) | Q(secondary_phone_number=phone)
        )
        return JsonResponse({
            'found': True,
            'name': customer.customer_name,
            'phone': customer.phone_number,
            'current_credit': str(customer.current_credit),
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
        paid_amount = Decimal(str(data.get('paid_amount', 0)))
        total_amount = Decimal(str(data['total']))

        sale = Sale.objects.create(
            customer=customer,
            cashier=request.user.profile,
            subtotal=Decimal(str(data['subtotal'])),
            discount=Decimal(str(data.get('discount', 0))),
            discount_percent=Decimal(str(data.get('discount_percent', 0))),
            tax=Decimal(str(data['tax'])),
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
                unit_price=Decimal(str(item['price'])),
                discount_percent=Decimal(str(item.get('discount', 0))),
                line_total=Decimal(str(item['line_total'])),
            )
            
            inventory, _ = Inventory.objects.get_or_create(product=product, defaults={'quantity_in_stock': 0})
            inventory.quantity_in_stock -= int(item['quantity'])
            inventory.save()
        
        if customer:
            from customers.models import CreditTransaction
            due_amount = total_amount - paid_amount
            if due_amount > 0:
                customer.current_credit += due_amount
                customer.save()
                CreditTransaction.objects.create(
                    customer=customer,
                    transaction_type='purchase',
                    amount=due_amount,
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
    amount_in_words = number_to_words(sale.total_amount)
    return render(request, 'sales/receipt.html', {
        'sale': sale,
        'amount_in_words': amount_in_words,
    })

@login_required
def receipt_pdf(request, sale_number):
    sale = get_object_or_404(Sale, sale_number=sale_number)
    buffer = generate_receipt_pdf(sale)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    disposition = 'attachment' if request.GET.get('download') == '1' else 'inline'
    response['Content-Disposition'] = f'{disposition}; filename="receipt_{sale_number}.pdf"'
    return response

@login_required
def sales_list(request):
    sales = Sale.objects.select_related('customer').all()
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    query = request.GET.get('q', '').strip()
    filter_by = request.GET.get('filter_by', 'customer')
    sort_by = request.GET.get('sort_by', 'date')
    
    if from_date:
        sales = sales.filter(sale_date__date__gte=from_date)
    if to_date:
        sales = sales.filter(sale_date__date__lte=to_date)

    if query:
        if filter_by == 'phone':
            sales = sales.filter(customer__phone_number__icontains=query)
        elif filter_by == 'sale_number':
            sales = sales.filter(sale_number__icontains=query)
        else:
            sales = sales.filter(customer__customer_name__icontains=query)

    if sort_by == 'customer':
        sales = sales.order_by('customer__customer_name', '-sale_date')
    elif sort_by == 'phone':
        sales = sales.order_by('customer__phone_number', '-sale_date')
    else:
        sales = sales.order_by('-sale_date')
    
    return render(request, 'sales/sales_list.html', {
        'sales': sales,
        'from_date': from_date,
        'to_date': to_date,
        'query': query,
        'filter_by': filter_by,
        'sort_by': sort_by,
    })


@login_required
def credit_records(request):
    customers = Customer.objects.filter(current_credit__gt=0).order_by('-current_credit')
    return render(request, 'sales/credit_records.html', {
        'customers': customers,
    })

@login_required
def sales_detail(request, sale_number):
    sale = get_object_or_404(Sale, sale_number=sale_number)
    return render(request, 'sales/sales_detail.html', {'sale': sale})

@login_required
def sales_edit(request, sale_number):
    sale = get_object_or_404(Sale, sale_number=sale_number)
    if request.method == 'POST':
        sale.payment_method = request.POST.get('payment_method', sale.payment_method)
        sale.paid_amount = Decimal(str(request.POST.get('paid_amount', sale.paid_amount)))
        sale.notes = request.POST.get('notes', '')
        sale.payment_status = 'paid' if sale.paid_amount >= sale.total_amount else 'partial'
        sale.save()
        messages.success(request, 'Sale updated successfully.')
        return redirect('sales_list')
    return render(request, 'sales/sales_edit.html', {'sale': sale})

@login_required
@transaction.atomic
def sales_delete(request, sale_number):
    sale = get_object_or_404(Sale, sale_number=sale_number)
    if request.method == 'POST':
        password = request.POST.get('admin_password', '')
        if not request.user.is_staff:
            messages.error(request, 'Admin access is required to delete a sale.')
        elif not password:
            messages.error(request, 'Admin password is required to delete a sale.')
        elif not request.user.check_password(password):
            messages.error(request, 'Invalid admin password.')
        else:
            for item in sale.items.all():
                inventory, _ = Inventory.objects.get_or_create(
                    product=item.product,
                    defaults={'quantity_in_stock': 0}
                )
                inventory.quantity_in_stock += item.quantity
                inventory.save()

            if sale.customer and sale.payment_method == 'credit':
                from customers.models import CreditTransaction
                sale.customer.current_credit -= sale.total_amount
                sale.customer.save()
                CreditTransaction.objects.create(
                    customer=sale.customer,
                    transaction_type='refund',
                    amount=sale.total_amount,
                    balance_after=sale.customer.current_credit,
                    related_sale=sale,
                )

            sale.delete()
            messages.success(request, 'Sale deleted successfully.')
            return redirect('sales_list')
    return render(request, 'sales/sales_delete.html', {'sale': sale})
