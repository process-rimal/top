
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vendor, VendorContact

@login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    context = {'vendors': vendors}
    return render(request, 'vendors/vendor_list.html', context)

@login_required
def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    contacts = VendorContact.objects.filter(vendor=vendor)
    context = {
        'vendor': vendor,
        'contacts': contacts
    }
    return render(request, 'vendors/vendor_detail.html', context)

@login_required
def vendor_add(request):
    if request.method == 'POST':
        vendor_name = request.POST.get('vendor_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        
        vendor = Vendor.objects.create(
            vendor_name=vendor_name,
            email=email,
            phone=phone,
            address=address,
            city=city
        )
        return redirect('vendor_detail', vendor_id=vendor.id)
    
    return render(request, 'vendors/vendor_add.html')

@login_required
def vendor_edit(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == 'POST':
        vendor.vendor_name = request.POST.get('vendor_name')
        vendor.email = request.POST.get('email')
        vendor.phone = request.POST.get('phone')
        vendor.address = request.POST.get('address')
        vendor.city = request.POST.get('city')
        vendor.save()
        return redirect('vendor_detail', vendor_id=vendor.id)
    
    context = {'vendor': vendor}
    return render(request, 'vendors/vendor_edit.html', context)

@login_required
def vendor_delete(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == 'POST':
        vendor.delete()
        return redirect('vendor_list')
    
    context = {'vendor': vendor}
    return render(request, 'vendors/vendor_delete.html', context)

@login_required
def add_vendor_contact(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == 'POST':
        contact_name = request.POST.get('contact_name')
        contact_phone = request.POST.get('contact_phone')
        contact_email = request.POST.get('contact_email')
        
        VendorContact.objects.create(
            vendor=vendor,
            contact_name=contact_name,
            contact_phone=contact_phone,
            contact_email=contact_email
        )
        return redirect('vendor_detail', vendor_id=vendor.id)
    
    context = {'vendor': vendor}
    return render(request, 'vendors/add_contact.html', context)
