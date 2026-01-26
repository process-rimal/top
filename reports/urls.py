from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_report, name='dashboard'),
    path('sales/', views.sales_report, name='sales_report'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('profit-loss/', views.profit_loss_report, name='profit_loss_report'),
    path('top-products/', views.top_products_report, name='top_products_report'),
    path('customer-purchases/', views.customer_purchase_report, name='customer_purchase_report'),
    path('daily-trend/', views.daily_sales_trend, name='daily_sales_trend'),
    path('dashboard/', views.dashboard_report, name='dashboard_report'),
]
