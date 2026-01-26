
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Customer, CustomerContact

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    search = request.GET.get('search')
    if search:
        customers = customers.filter(customer_name__icontains=search)
    
    context = {'customers': customers}
    return render(request, 'customers/customer_list.html', context)

@login_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    contacts = CustomerContact.objects.filter(customer=customer)
    context = {
        'customer': customer,
        'contacts': contacts
    }
    return render(request, 'customers/customer_detail.html', context)

@login_required
def customer_add(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        customer_type = request.POST.get('customer_type')
        
        customer = Customer.objects.create(
            customer_name=customer_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            customer_type=customer_type
        )
        return redirect('customer_detail', customer_id=customer.id)
    
    return render(request, 'customers/customer_add.html')

@login_required
def customer_edit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.customer_name = request.POST.get('customer_name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone')
        customer.address = request.POST.get('address')
        customer.city = request.POST.get('city')
        customer.customer_type = request.POST.get('customer_type')
        customer.save()
        return redirect('customer_detail', customer_id=customer.id)
    
    context = {'customer': customer}
    return render(request, 'customers/customer_edit.html', context)

@login_required
def customer_delete(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    
    context = {'customer': customer}
    return render(request, 'customers/customer_delete.html', context)

@login_required
def customer_credit_limit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.credit_limit = request.POST.get('credit_limit')
        customer.save()
        return redirect('customer_detail', customer_id=customer.id)
    
    context = {'customer': customer}
    return render(request, 'customers/credit_limit.html', context)
