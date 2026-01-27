from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vendor, PurchaseOrder, PurchaseOrderItem

@login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, 'vendors/vendor_list.html', {'vendors': vendors})

@login_required
def vendor_add(request):
    if request.method == 'POST':
        Vendor.objects.create(
            vendor_id=request.POST.get('vendor_id'),
            name=request.POST.get('name'),
            contact_person=request.POST.get('contact_person', ''),
            phone=request.POST.get('phone'),
            email=request.POST.get('email', ''),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            payment_terms=request.POST.get('payment_terms', ''),
            is_active=bool(request.POST.get('is_active')),
        )
        return redirect('vendor_list')
    return render(request, 'vendors/vendor_add.html')

@login_required
def vendor_edit(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.name = request.POST.get('name')
        vendor.contact_person = request.POST.get('contact_person', '')
        vendor.phone = request.POST.get('phone')
        vendor.email = request.POST.get('email', '')
        vendor.address = request.POST.get('address')
        vendor.city = request.POST.get('city')
        vendor.payment_terms = request.POST.get('payment_terms', '')
        vendor.is_active = bool(request.POST.get('is_active'))
        vendor.save()
        return redirect('vendor_list')
    return render(request, 'vendors/vendor_edit.html', {'vendor': vendor})

@login_required
def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        password = request.POST.get('admin_password', '')
        if not request.user.is_staff:
            messages.error(request, 'Admin access is required to delete a vendor.')
        elif not password:
            messages.error(request, 'Admin password is required to delete a vendor.')
        elif not request.user.check_password(password):
            messages.error(request, 'Invalid admin password.')
        else:
            vendor.delete()
            messages.success(request, 'Vendor deleted successfully.')
            return redirect('vendor_list')
    return render(request, 'vendors/vendor_delete.html', {'vendor': vendor})

@login_required
def purchase_order_list(request):
    pos = PurchaseOrder.objects.all()
    return render(request, 'vendors/purchase_order_list.html', {'purchase_orders': pos})

@login_required
def purchase_order_add(request):
    return render(request, 'vendors/purchase_order_add.html')

@login_required
def purchase_order_detail(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'vendors/purchase_order_detail.html', {'po': po})

@login_required
def purchase_order_receive(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'vendors/purchase_order_receive.html', {'po': po})
