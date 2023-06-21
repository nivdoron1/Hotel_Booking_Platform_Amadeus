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

