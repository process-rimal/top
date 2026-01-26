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
