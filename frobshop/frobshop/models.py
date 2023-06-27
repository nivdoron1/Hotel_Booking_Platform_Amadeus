from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField()
    booking_confirmation = models.CharField(max_length=255)
    Booking_ID = models.CharField(max_length=255)
    Provider_Confirmation_ID = models.CharField(max_length=255)
    Reference_ID = models.CharField(max_length=255)
    Origin_System_Code = models.CharField(max_length=255)


from oscar.apps.catalogue.models import Product


class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    summary = models.CharField(max_length=200)
    parent = models.CharField(max_length=200)


class Payment(models.Model):
    title = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    method = models.CharField(max_length=100)
    vendor_code = models.CharField(max_length=50)
    card_token = models.CharField(max_length=200)  # This will be provided by the payment gateway
    expiry_date = models.DateField()
