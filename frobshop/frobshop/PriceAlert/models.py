from django.db import models
from django.contrib.auth.models import User


class PriceAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_alerts')
    hotel_name = models.CharField(max_length=200)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_adults = models.IntegerField()
    number_of_rooms = models.IntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    email = models.EmailField()  # The new email field
    hotel_id = models.CharField(max_length=200)

    class Meta:
        db_table = 'PriceAlert_pricealert'
