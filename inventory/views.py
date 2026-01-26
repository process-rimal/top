from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
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
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    inventory = Inventory.objects.get(product=product)
    context = {
        'product': product,
        'inventory': inventory
    }
    return render(request, 'inventory/product_detail.html', context)

@login_required
def product_add(request):
    if request.method == 'POST':
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
        
        Inventory.objects.create(product=product)
        return redirect('product_list')
    
    context = {'categories': Category.objects.all()}
    return render(request, 'inventory/product_add.html', context)

@login_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.category_id = request.POST.get('category')
        product.cost_price = request.POST.get('cost_price')
        product.selling_price = request.POST.get('selling_price')
        product.save()
        return redirect('product_detail', product_id=product.id)
    
    context = {
        'product': product,
        'categories': Category.objects.all()
    }
    return render(request, 'inventory/product_edit.html', context)

@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    
    context = {'product': product}
    return render(request, 'inventory/product_delete.html', context)

@login_required
def category_list(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'inventory/category_list.html', context)

@login_required
def category_add(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        Category.objects.create(category_name=category_name)
        return redirect('category_list')
    
    return render(request, 'inventory/category_add.html')

@login_required
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.category_name = request.POST.get('category_name')
        category.save()
        return redirect('category_list')
    
    context = {'category': category}
    return render(request, 'inventory/category_edit.html', context)

@login_required
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    
    context = {'category': category}
    return render(request, 'inventory/category_delete.html', context)

@login_required
def generate_barcode(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    barcode_format = barcode.get_barcode_class('code128')
    barcode_obj = barcode_format(str(product.sku), writer=ImageWriter())
    
    buffer = io.BytesIO()
    barcode_obj.write(buffer)
    buffer.seek(0)
    
    return HttpResponse(buffer.getvalue(), content_type='image/png')

@login_required
def low_stock_report(request):
    low_stock_items = Inventory.objects.filter(quantity__lt=10)
    context = {'items': low_stock_items}
    return render(request, 'inventory/low_stock.html', context)
