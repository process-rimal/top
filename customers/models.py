from django.db import models
from django.core.validators import RegexValidator

class Customer(models.Model):
    """Customer Database - Mobile number as primary identifier"""
    
    phone_regex = RegexValidator(
        regex=r'^(?:\+977|977)?9\d{8,9}$',  # Nepal phone format (optional country code)
        message="Enter valid Nepal mobile number",
    )
    
    # Nepal format: +977XXXXXXXXXX or 9XXXXXXXXX
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[phone_regex],
        db_index=True
    )
    
    customer_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    
    # Credit Management
    total_credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loyalty_points = models.IntegerField(default=0)
    
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        ordering = ['customer_name']
        indexes = [
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return f"{self.customer_name} ({self.phone_number})"
    
    @property
    def available_credit(self):
        """Available credit = Total limit - Current debt"""
        return self.total_credit_limit - self.current_credit
    
    @property
    def credit_status(self):
        """Check credit status"""
        if self.current_credit >= self.total_credit_limit:
            return 'exceeded'
        elif self.current_credit > (self.total_credit_limit * 0.8):
            return 'warning'
        else:
            return 'good'


class CreditTransaction(models.Model):
    """Credit Transaction History"""
    
    TRANSACTION_TYPE = [
        ('purchase', 'Purchase'),
        ('payment', 'Payment Received'),
        ('adjustment', 'Credit Adjustment'),
        ('refund', 'Refund'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='credit_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)  # Running balance
    
    description = models.TextField(blank=True)
    related_sale = models.ForeignKey('sales.Sale', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_by = models.ForeignKey('accounts.UserProfile', on_delete=models.SET_NULL, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'credit_transactions'
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.customer.customer_name} - {self.transaction_type}"
