from django.db import models

class Vendor(models.Model):
    vendor_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.vendor_name

class VendorContact(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='contacts')
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.contact_name} - {self.vendor.vendor_name}"
