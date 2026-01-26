from django.db import models

class Customer(models.Model):
    CUSTOMER_TYPES = [
        ('walk_in', 'Walk-in'),
        ('regular', 'Regular'),
        ('wholesale', 'Wholesale'),
    ]
    
    customer_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='regular')
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.customer_name

class CustomerContact(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contacts')
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.contact_name} - {self.customer.customer_name}"
