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
