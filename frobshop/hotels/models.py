from django.db import models


class Hotel(models.Model):
    hotel_id = models.CharField(max_length=200, unique=True)
    hotel_name = models.CharField(max_length=200)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    image = models.ForeignKey('Image', on_delete=models.CASCADE, null=True, blank=True)

class Image(models.Model):
    data = models.BinaryField()