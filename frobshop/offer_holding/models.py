from django.db import models


class OfferInformation(models.Model):
    username = models.CharField(max_length=100)
    offer_id = models.CharField(max_length=100)  # or ForeignKey to Offer model if you have one
    title = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    payment_method = models.CharField(max_length=100)
    card_vendor_code = models.CharField(max_length=20)  # Consider encrypting
    card_number = models.BinaryField(max_length=512)  # Consider encrypting
    card_expiry_date = models.CharField(max_length=7, help_text="Format: MM/YYYY")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Offer Information"
        verbose_name_plural = "Offer Informations"
