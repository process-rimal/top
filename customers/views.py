from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Customer, CreditTransaction

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customers/customer_list.html', {'customers': customers})

@login_required
def customer_add(request):
    if request.method == 'POST':
        Customer.objects.create(
            phone_number=request.POST.get('phone_number'),
            customer_name=request.POST.get('customer_name'),
            email=request.POST.get('email', ''),
            address=request.POST.get('address', ''),
            city=request.POST.get('city', ''),
            total_credit_limit=request.POST.get('total_credit_limit') or 0
        )
        return redirect('customer_list')
    return render(request, 'customers/customer_add.html')

@login_required
def customer_detail(request, phone):
    customer = get_object_or_404(Customer, phone_number=phone)
    return render(request, 'customers/customer_detail.html', {'customer': customer})

@login_required
def customer_edit(request, phone):
    customer = get_object_or_404(Customer, phone_number=phone)
    if request.method == 'POST':
        customer.customer_name = request.POST.get('customer_name')
        customer.email = request.POST.get('email')
        customer.save()
        return redirect('customer_detail', phone=phone)
    return render(request, 'customers/customer_edit.html', {'customer': customer})

@login_required
def customer_credit_history(request, phone):
    customer = get_object_or_404(Customer, phone_number=phone)
    transactions = customer.credit_transactions.all()
    return render(request, 'customers/credit_history.html', {
        'customer': customer,
        'transactions': transactions
    })
