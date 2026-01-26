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
        barcode_value = request.POST.get('barcode') or ''
        wholesale_price = request.POST.get('wholesale_price') or None
        unit = request.POST.get('unit') or 'piece'
        reorder_level = request.POST.get('reorder_level') or 10
        initial_quantity = int(request.POST.get('quantity_in_stock') or 0)
        
        category = Category.objects.get(id=category_id)
        product = Product.objects.create(
            sku=sku,
            product_name=product_name,
            category=category,
            cost_price=cost_price,
            selling_price=selling_price,
            barcode=barcode_value,
            wholesale_price=wholesale_price,
            unit=unit,
            reorder_level=reorder_level,
        )
        
        Inventory.objects.create(product=product, quantity_in_stock=initial_quantity)
        return redirect('product_list')
    
    context = {'categories': Category.objects.all()}
    return render(request, 'inventory/product_add.html', context)

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, id=pk)
    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.category_id = request.POST.get('category')
        product.cost_price = request.POST.get('cost_price')
        product.selling_price = request.POST.get('selling_price')
        product.barcode = request.POST.get('barcode') or ''
        product.wholesale_price = request.POST.get('wholesale_price') or None
        product.unit = request.POST.get('unit') or product.unit
        product.reorder_level = request.POST.get('reorder_level') or product.reorder_level
        product.save()
        return redirect('product_list')
    
    context = {
        'product': product,
        'categories': Category.objects.all()
    }
    return render(request, 'inventory/product_edit.html', context)

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, id=pk)
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
        name = request.POST.get('name')
        category_type = request.POST.get('category_type')
        Category.objects.create(name=name, category_type=category_type)
        return redirect('category_list')
    
    return render(request, 'inventory/category_add.html')

@login_required
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.category_type = request.POST.get('category_type')
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
    low_stock_items = Inventory.objects.filter(quantity_in_stock__lt=10)
    context = {'items': low_stock_items}
    return render(request, 'inventory/low_stock.html', context)

@login_required
def inventory_list(request):
    inventory_items = Inventory.objects.select_related('product').all()
    context = {'inventory_items': inventory_items}
    return render(request, 'inventory/inventory_list.html', context)

@login_required
def inventory_detail(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    context = {'inventory': inventory}
    return render(request, 'inventory/inventory_detail.html', context)

@login_required
def stock_adjust(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        adjustment = int(request.POST.get('adjustment', 0))
        inventory.quantity_in_stock += adjustment
        inventory.save()
        return redirect('inventory_detail', pk=pk)
    context = {'inventory': inventory}
    return render(request, 'inventory/stock_adjust.html', context)
