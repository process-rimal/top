from django.urls import path
from . import views

urlpatterns = [
    path('', views.sale_list, name='sales_list'),
    path('pos/', views.pos_system, name='pos_system'),
    path('create/', views.create_sale, name='create_sale'),
    path('list/', views.sale_list, name='sale_list'),
    path('<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('<int:sale_id>/receipt/', views.generate_receipt, name='generate_receipt'),
    path('daily/', views.daily_sales, name='daily_sales'),
    path('by-date/', views.sales_by_date, name='sales_by_date'),
]
