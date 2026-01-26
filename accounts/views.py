from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django import forms
from .models import UserProfile

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

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

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
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Auto-create profile if it doesn't exist
        user_profile = UserProfile.objects.create(
            user=request.user,
            role='staff'  # Default role
        )
    
    # Get summary data for dashboard
    from inventory.models import Product, Inventory
    from sales.models import Sale
    from customers.models import Customer
    from django.utils import timezone
    from django.db.models import F
    
    context = {
        'user_profile': user_profile,
        'total_products': Product.objects.count(),
        'low_stock_items': Inventory.objects.filter(quantity_in_stock__lte=F('product__reorder_level')).count(),
        'total_customers': Customer.objects.count(),
        'today_sales': Sale.objects.filter(sale_date__date=timezone.now().date()).count(),
    }
    return render(request, 'reports/dashboard.html', context)

@login_required
def profile(request):
    try:
        profile_obj = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile_obj = UserProfile.objects.create(user=request.user, role='staff')
    
    if request.method == 'POST':
        profile_obj.phone = request.POST.get('phone')
        profile_obj.address = request.POST.get('address')
        profile_obj.city = request.POST.get('city')
        profile_obj.save()
        return redirect('dashboard')
    return render(request, 'accounts/profile.html', {'profile': profile_obj})
