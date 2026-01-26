from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class UserProfile(models.Model):
    """Extended user profile with shop-specific information"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Shop Staff'),
        ('manager', 'Manager'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_profile'
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"
