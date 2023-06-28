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


from django.db import models
from django.core.mail import send_mail
from django.dispatch import Signal, receiver

# Define your signal
user_registered = Signal(providing_args=["user", "request"])


# Define your email sending function
def send_registration_email(user):
    subject = "Registration Complete"
    message = "Welcome to our site, {}. Your registration is complete.".format(user.username)
    from_email = 'your_email@example.com'
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)


from django.dispatch import receiver
from oscar.apps.customer.signals import user_registered
from .email_utils import send_registration_email


@receiver(user_registered)
def send_welcome_email(sender, user, request, **kwargs):
    send_registration_email(user)
