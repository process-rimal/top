# shop_management/urls.py - Main URL Configuration

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),          # User authentication
    path('inventory/', include('inventory.urls')), # Products & Stock
    path('vendors/', include('vendors.urls')),    # Vendor management
    path('customers/', include('customers.urls')), # Customer records
    path('sales/', include('sales.urls')),        # POS & Billing
    path('reports/', include('reports.urls')),    # Reports
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# ========================================
# accounts/urls.py - Authentication URLs

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', auth_views.PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),
]


# ========================================
# inventory/urls.py - Product & Stock URLs

from django.urls import path
from . import views

urlpatterns = [
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    
    # Inventory URLs
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/<int:pk>/', views.inventory_detail, name='inventory_detail'),
    path('inventory/<int:pk>/adjust/', views.stock_adjust, name='stock_adjust'),
    
    # Barcode
    path('barcode/<int:product_id>/', views.generate_barcode, name='generate_barcode'),
]


# ========================================
# vendors/urls.py - Vendor URLs

from django.urls import path
from . import views

urlpatterns = [
    # Vendor URLs
    path('', views.vendor_list, name='vendor_list'),
    path('add/', views.vendor_add, name='vendor_add'),
    path('<int:pk>/edit/', views.vendor_edit, name='vendor_edit'),
    path('<int:pk>/delete/', views.vendor_delete, name='vendor_delete'),
    
    # Purchase Order URLs
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/add/', views.purchase_order_add, name='purchase_order_add'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('purchase-orders/<int:pk>/receive/', views.purchase_order_receive, name='purchase_order_receive'),
]


# ========================================
# customers/urls.py - Customer URLs

from django.urls import path
from . import views

urlpatterns = [
    # Customer URLs
    path('', views.customer_list, name='customer_list'),
    path('add/', views.customer_add, name='customer_add'),
    path('<str:phone>/', views.customer_detail, name='customer_detail'),
    path('<str:phone>/edit/', views.customer_edit, name='customer_edit'),
    path('<str:phone>/credit/', views.customer_credit_history, name='customer_credit_history'),
]


# ========================================
# sales/urls.py - Sales/POS URLs

from django.urls import path
from . import views

urlpatterns = [
    # POS & Billing
    path('pos/', views.pos_view, name='pos'),
    path('api/search-product/', views.search_product_api, name='search_product_api'),
    path('api/get-customer/', views.get_customer_api, name='get_customer_api'),
    path('api/create-sale/', views.create_sale_api, name='create_sale_api'),
    
    # Receipt & Invoice
    path('receipt/<str:sale_number>/', views.print_receipt, name='print_receipt'),
    path('receipt/<str:sale_number>/pdf/', views.receipt_pdf, name='receipt_pdf'),
    
    # Sales History
    path('history/', views.sales_list, name='sales_list'),
    path('<str:sale_number>/', views.sales_detail, name='sales_detail'),
]


# ========================================
# reports/urls.py - Reports URLs

from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('sales/', views.sales_report, name='sales_report'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('customers/', views.customer_report, name='customer_report'),
    path('vendors/', views.vendor_report, name='vendor_report'),
    
    # Export
    path('sales/export/', views.export_sales, name='export_sales'),
    path('inventory/export/', views.export_inventory, name='export_inventory'),
]


# ========================================
# accounts/views.py - Authentication Views

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile
from django import forms

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    
    class Meta:
        model = User
        fields = ('username', 'email')
    
    def clean(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('password2'):
            raise forms.ValidationError('Passwords do not match')
        return self.cleaned_data

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create UserProfile
            UserProfile.objects.create(user=user, role='staff')
            
            # Login user
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    # Get summary data for dashboard
    from inventory.models import Product, Inventory
    from sales.models import Sale
    from customers.models import Customer
    
    context = {
        'total_products': Product.objects.count(),
        'low_stock_items': Inventory.objects.filter(quantity_in_stock__lt=models.F('product__reorder_level')).count(),
        'total_customers': Customer.objects.count(),
        'today_sales': Sale.objects.filter(sale_date__date=timezone.now().date()).count(),
        'total_revenue': Sale.objects.aggregate(models.Sum('total_amount'))['total_amount__sum'] or 0,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.city = request.POST.get('city')
        profile.save()
        return redirect('dashboard')
    return render(request, 'accounts/profile.html', {'profile': profile})


# ========================================
# inventory/views.py - Product Views (Sample)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Product, Category, Inventory
import barcode
from barcode.writer import ImageWriter
import io

@login_required
def product_list(request):
    products = Product.objects.all()
    category = request.GET.get('category')
    if category:
        products = products.filter(category__id=category)
    
    context = {
        'products': products,
        'categories': Category.objects.all()
    }
    return render(request, 'inventory/products_list.html', context)

@login_required
def product_add(request):
    if request.method == 'POST':
        # Handle form submission
        sku = request.POST.get('sku')
        product_name = request.POST.get('product_name')
        category_id = request.POST.get('category')
        cost_price = request.POST.get('cost_price')
        selling_price = request.POST.get('selling_price')
        
        category = Category.objects.get(id=category_id)
        product = Product.objects.create(
            sku=sku,
            product_name=product_name,
            category=category,
            cost_price=cost_price,
            selling_price=selling_price
        )
        
        # Create inventory record
        Inventory.objects.create(product=product)
        
        return redirect('product_list')
    
    context = {'categories': Category.objects.all()}
    return render(request, 'inventory/product_add.html', context)

@login_required
def generate_barcode(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Generate barcode
    barcode_format = barcode.get_barcode_class('code128')
    barcode_obj = barcode_format(str(product.sku), writer=ImageWriter())
    
    # Save to bytes
    buffer = io.BytesIO()
    barcode_obj.write(buffer)
    buffer.seek(0)
    
    return HttpResponse(buffer.getvalue(), content_type='image/png')

# Similar views for product_edit, product_delete, category_list, etc.
# ... (Follow the same pattern)
