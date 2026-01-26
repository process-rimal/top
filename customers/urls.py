from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('add/', views.customer_add, name='customer_add'),
    path('<int:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('<int:customer_id>/delete/', views.customer_delete, name='customer_delete'),
    path('<int:customer_id>/credit-limit/', views.customer_credit_limit, name='customer_credit_limit'),
]
