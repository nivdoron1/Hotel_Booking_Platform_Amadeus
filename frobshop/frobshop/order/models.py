from django.db import models
from oscar.apps.order.abstract_models import AbstractOrder


class Order(AbstractOrder):
    Booking_ID = models.CharField(max_length=200, null=True, blank=True)
    Provider_Confirmation_ID = models.CharField(max_length=200, null=True, blank=True)
    Reference_ID = models.CharField(max_length=200, null=True, blank=True)
    Origin_System_Code = models.CharField(max_length=200, null=True, blank=True)


from oscar.apps.order.models import *  # noqa isort:skip
