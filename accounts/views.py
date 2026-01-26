from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import UserProfile

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/admin/')  # Django admin dashboard

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    context = {'user_profile': user_profile}
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    context = {'user_profile': user_profile}
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_update(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        user_profile.phone = request.POST.get('phone')
        user_profile.address = request.POST.get('address')
        user_profile.city = request.POST.get('city')
        user_profile.save()
        return redirect('profile')
    context = {'user_profile': user_profile}
    return render(request, 'accounts/profile_edit.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        user = request.user
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            login(request, user)
            return redirect('dashboard')
    return render(request, 'accounts/change_password.html')
