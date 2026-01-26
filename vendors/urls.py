from django.urls import path
from . import views

urlpatterns = [
    path('', views.vendor_list, name='vendor_list'),
    path('<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    path('add/', views.vendor_add, name='vendor_add'),
    path('<int:vendor_id>/edit/', views.vendor_edit, name='vendor_edit'),
    path('<int:vendor_id>/delete/', views.vendor_delete, name='vendor_delete'),
    path('<int:vendor_id>/contact/add/', views.add_vendor_contact, name='add_vendor_contact'),
]
