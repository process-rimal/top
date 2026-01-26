from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city')
        )
        return redirect('vendor_list')
    return render(request, 'vendors/vendor_add.html')

@login_required
def vendor_edit(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.name = request.POST.get('name')
        vendor.phone = request.POST.get('phone')
        vendor.save()
        return redirect('vendor_list')
    return render(request, 'vendors/vendor_edit.html', {'vendor': vendor})

@login_required
def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.delete()
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
