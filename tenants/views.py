from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Tenant
from accounts.models import UserProfile
from tenants.utils import (
    set_current_tenant, provision_tenant_database,
    migrate_tenant_database, ensure_tenant_schema
)


def is_superadmin(user):
    """Check if user is superadmin"""
    if not user or not user.is_authenticated:
        return False
    try:
        return user.profile.role == 'superadmin'
    except UserProfile.DoesNotExist:
        return False


def superadmin_required(view_func):
    """Decorator to require superadmin role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_superadmin(request.user):
            messages.error(request, 'Access denied. Superadmin privileges required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@superadmin_required
def superadmin_dashboard(request):
    """Superadmin dashboard - manage all vendors"""
    vendors = Tenant.objects.all().order_by('-created_at')
    
    context = {
        'vendors': vendors,
        'total_vendors': vendors.count(),
        'active_vendors': vendors.filter(is_active=True).count(),
        'inactive_vendors': vendors.filter(is_active=False).count(),
    }
    return render(request, 'tenants/superadmin_dashboard.html', context)


@login_required
@superadmin_required
def create_vendor(request):
    """Create a new vendor (shop/tenant) - superadmin only"""
    if request.method == 'POST':
        original_tenant = getattr(request, 'tenant', None)
        original_db_alias = getattr(request, 'tenant_db', None)
        set_current_tenant(None, None)
        try:
            vendor_name = request.POST.get('vendor_name', '').strip()
            vendor_code = request.POST.get('vendor_code', '').strip().lower()
            owner_email = request.POST.get('owner_email', '').strip().lower()
            admin_password = request.POST.get('admin_password', '').strip()
            admin_password2 = request.POST.get('admin_password2', '').strip()
            
            # Validation
            if not all([vendor_name, vendor_code, owner_email, admin_password]):
                messages.error(request, 'All fields are required.')
                return render(request, 'tenants/create_vendor.html')
            
            if admin_password != admin_password2:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'tenants/create_vendor.html')
            
            if Tenant.objects.filter(code__iexact=vendor_code).exists():
                messages.error(request, 'Vendor code already exists.')
                return render(request, 'tenants/create_vendor.html')
            
            if User.objects.filter(email__iexact=owner_email).exists():
                messages.error(request, 'Email already registered.')
                return render(request, 'tenants/create_vendor.html')
            
            try:
                admin_user = User.objects.using('default').create_user(
                    username=owner_email,
                    email=owner_email,
                    password=admin_password,
                    is_staff=True,
                )
                db_name = f"shop_{vendor_code}"
                tenant = Tenant.objects.using('default').create(
                    name=vendor_name,
                    code=vendor_code,
                    owner_email=owner_email,
                    db_name=db_name,
                    admin_user=admin_user,
                )

                UserProfile.objects.using('default').create(
                    user=admin_user,
                    role='tenant_admin',
                    tenant=tenant,
                )
                
                # Provision and migrate tenant database
                provision_tenant_database(tenant)
                migrate_tenant_database(tenant)
                
                # Create admin user in tenant database
                db_alias = ensure_tenant_schema(tenant)
                set_current_tenant(tenant, db_alias)
                try:
                    from django.contrib.auth import get_user_model

                    UserModel = get_user_model()
                    tenant_admin = UserModel._default_manager.db_manager(db_alias).create_user(
                        username=owner_email,
                        email=owner_email,
                        password=admin_password,
                        is_staff=True,
                        is_superuser=True,
                    )
                    UserProfile.objects.using(db_alias).create(
                        user=tenant_admin,
                        role='tenant_admin',
                        tenant_id=tenant.id,
                    )
                finally:
                    set_current_tenant(None, None)
                
                messages.success(request, f'Vendor "{vendor_name}" created successfully.')
                return redirect('superadmin_dashboard')
            
            except Exception as e:
                messages.error(request, f'Error creating vendor: {str(e)}')
                # Clean up if something went wrong
                if 'admin_user' in locals():
                    admin_user.delete(using='default')
                if 'tenant' in locals():
                    tenant.delete(using='default')
                return render(request, 'tenants/create_vendor.html')
        finally:
            if original_tenant and original_db_alias:
                set_current_tenant(original_tenant, original_db_alias)
            else:
                set_current_tenant(None, None)
    
    return render(request, 'tenants/create_vendor.html')


@login_required
@superadmin_required
def vendor_detail(request, tenant_id):
    """View and edit vendor details"""
    vendor = get_object_or_404(Tenant, id=tenant_id)
    
    if request.method == 'POST':
        vendor.name = request.POST.get('name', vendor.name)
        vendor.status = request.POST.get('status', vendor.status)
        vendor.is_active = vendor.status == 'active'
        vendor.access_customers = request.POST.get('access_customers') == 'on'
        vendor.access_inventory = request.POST.get('access_inventory') == 'on'
        vendor.access_sales = request.POST.get('access_sales') == 'on'
        vendor.access_reports = request.POST.get('access_reports') == 'on'
        vendor.save()
        messages.success(request, 'Vendor updated successfully.')
        return redirect('vendor_detail', tenant_id=vendor.id)
    
    context = {
        'vendor': vendor,
        'admin_user': vendor.admin_user,
    }
    return render(request, 'tenants/vendor_detail.html', context)


@login_required
@superadmin_required
def deactivate_vendor(request, tenant_id):
    """Deactivate a vendor"""
    vendor = get_object_or_404(Tenant, id=tenant_id)
    
    if request.method == 'POST':
        vendor.is_active = False
        vendor.status = 'inactive'
        vendor.save()
        messages.success(request, f'Vendor "{vendor.name}" has been deactivated.')
        return redirect('superadmin_dashboard')
    
    context = {'vendor': vendor}
    return render(request, 'tenants/deactivate_vendor.html', context)


@login_required
@superadmin_required
def reset_vendor_password(request, tenant_id):
    """Reset vendor admin password"""
    vendor = get_object_or_404(Tenant, id=tenant_id)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        new_password2 = request.POST.get('new_password2', '').strip()
        
        if not new_password or new_password != new_password2:
            messages.error(request, 'Passwords do not match or are empty.')
            return redirect('reset_vendor_password', tenant_id=vendor.id)
        
        if vendor.admin_user:
            vendor.admin_user.set_password(new_password)
            vendor.admin_user.save()

            db_alias = ensure_tenant_schema(vendor)
            set_current_tenant(vendor, db_alias)
            try:
                from django.contrib.auth import get_user_model

                UserModel = get_user_model()
                tenant_admin = UserModel.objects.using(db_alias).filter(email__iexact=vendor.owner_email).first()
                if tenant_admin:
                    tenant_admin.set_password(new_password)
                    tenant_admin.save(using=db_alias)
            finally:
                set_current_tenant(None, None)

            messages.success(request, 'Password reset successfully.')
            return redirect('vendor_detail', tenant_id=vendor.id)
    
    context = {'vendor': vendor}
    return render(request, 'tenants/reset_vendor_password.html', context)


@login_required
def superadmin_login_as_vendor(request, tenant_id):
    """Allow superadmin to switch to vendor view"""
    if not is_superadmin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('login')
    
    vendor = get_object_or_404(Tenant, id=tenant_id)
    
    # Set vendor context for this session
    db_alias = ensure_tenant_schema(vendor)
    set_current_tenant(vendor, db_alias)
    request.session['tenant_id'] = vendor.id
    request.session['tenant_alias'] = db_alias
    request.session['superadmin_id'] = request.user.id  # Track which superadmin is viewing
    
    messages.info(request, f'Now viewing as: {vendor.name}')
    return redirect('dashboard')
