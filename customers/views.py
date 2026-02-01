from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Customer, CreditTransaction, IrregularCustomer
from sales.models import Sale

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    irregular_customers = IrregularCustomer.objects.all()
    query = request.GET.get('q', '').strip()
    filter_by = request.GET.get('filter_by', 'name')
    sort_by = request.GET.get('sort_by', 'name_asc')
    if query:
        if filter_by == 'phone':
            customers = customers.filter(
                Q(phone_number__icontains=query) |
                Q(secondary_phone_number__icontains=query)
            )
            irregular_customers = irregular_customers.filter(phone_number__icontains=query)
        elif filter_by == 'secondary_phone':
            customers = customers.filter(secondary_phone_number__icontains=query)
            irregular_customers = irregular_customers.none()
        elif filter_by == 'email':
            customers = customers.filter(email__icontains=query)
            irregular_customers = irregular_customers.none()
        elif filter_by == 'address':
            customers = customers.filter(Q(address__icontains=query) | Q(city__icontains=query))
            irregular_customers = irregular_customers.filter(address__icontains=query)
        elif filter_by == 'credit':
            try:
                credit_value = float(query)
                customers = customers.filter(current_credit=credit_value)
                irregular_customers = irregular_customers.none()
            except ValueError:
                customers = customers.none()
                irregular_customers = irregular_customers.none()
        elif filter_by == 'all':
            customers = customers.filter(
                Q(customer_name__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(secondary_phone_number__icontains=query) |
                Q(email__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query)
            )
            irregular_customers = irregular_customers.filter(
                Q(customer_name__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(address__icontains=query)
            )
        else:
            customers = customers.filter(customer_name__icontains=query)
            irregular_customers = irregular_customers.filter(customer_name__icontains=query)
    if sort_by == 'name_desc':
        customers = customers.order_by('-customer_name')
        irregular_customers = irregular_customers.order_by('-customer_name')
    elif sort_by == 'credit_asc':
        customers = customers.order_by('current_credit', 'customer_name')
        irregular_customers = irregular_customers.order_by('customer_name')
    elif sort_by == 'credit_desc':
        customers = customers.order_by('-current_credit', 'customer_name')
        irregular_customers = irregular_customers.order_by('customer_name')
    else:
        customers = customers.order_by('customer_name')
        irregular_customers = irregular_customers.order_by('customer_name')

    return render(request, 'customers/customer_list.html', {
        'customers': customers,
        'irregular_customers': irregular_customers,
        'query': query,
        'filter_by': filter_by,
        'sort_by': sort_by,
    })

@login_required
def customer_add(request):
    if request.method == 'POST':
        Customer.objects.create(
            phone_number=request.POST.get('phone_number'),
            secondary_phone_number=request.POST.get('secondary_phone_number', ''),
            customer_name=request.POST.get('customer_name'),
            email=request.POST.get('email', ''),
            address=request.POST.get('address', ''),
            city=request.POST.get('city', ''),
            notes=request.POST.get('notes', ''),
        )
        return redirect('customer_list')
    return render(request, 'customers/customer_add.html')

@login_required
def customer_detail(request, phone):
    customer = get_object_or_404(Customer, phone_number=phone)
    credit_transactions = customer.credit_transactions.select_related('related_sale').all()
    sales = customer.sales.all()
    return render(request, 'customers/customer_detail.html', {
        'customer': customer,
        'credit_transactions': credit_transactions,
        'sales': sales,
    })


@login_required
def irregular_customer_detail(request, pk):
    irregular_customer = get_object_or_404(IrregularCustomer, id=pk)
    sales = Sale.objects.filter(irregular_customer=irregular_customer).order_by('-sale_date')
    return render(request, 'customers/ir_customer_detail.html', {
        'irregular_customer': irregular_customer,
        'sales': sales,
    })

@login_required
def customer_edit(request, phone):
    customer = get_object_or_404(Customer, phone_number=phone)
    if request.method == 'POST':
        customer.customer_name = request.POST.get('customer_name')
        customer.email = request.POST.get('email')
        customer.secondary_phone_number = request.POST.get('secondary_phone_number', '')
        customer.address = request.POST.get('address', '')
        customer.city = request.POST.get('city', '')
        customer.notes = request.POST.get('notes', '')
        customer.save()
        return redirect('customer_detail', phone=phone)
    return render(request, 'customers/customer_edit.html', {'customer': customer})

@login_required
def customer_delete(request, phone):
    customer = get_object_or_404(Customer, phone_number=phone)
    if request.method == 'POST':
        password = request.POST.get('admin_password', '')
        if not request.user.is_staff:
            messages.error(request, 'Admin access is required to delete a customer.')
        elif not password:
            messages.error(request, 'Admin password is required to delete a customer.')
        elif not request.user.check_password(password):
            messages.error(request, 'Invalid admin password.')
        else:
            customer.delete()
            messages.success(request, 'Customer deleted successfully.')
            return redirect('customer_list')
    return render(request, 'customers/customer_delete.html', {'customer': customer})

@login_required
def customer_credit_history(request, phone):
    customer = get_object_or_404(Customer, phone_number=phone)
    transactions = customer.credit_transactions.all()
    return render(request, 'customers/credit_history.html', {
        'customer': customer,
        'transactions': transactions
    })
