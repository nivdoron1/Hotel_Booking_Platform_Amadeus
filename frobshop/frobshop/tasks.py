from __future__ import absolute_import,unicode_literals

from celery import shared_task
from .PriceAlert.models import PriceAlert
# Other necessary imports like for fetching hotel offers
from .views import get_hotel_offer, SimulatedRequest
# tasks.py
from celery import shared_task

@shared_task
def hello_task():
    print("hello")


"""
@shared_task
def get_hotel_offer_task(user_email, alert_id):
    # You might need some imports here
    request = SimulatedRequest(user_email)
    get_hotel_offer(request, alert_id)
    
@shared_task
def get_hotel_offer_task(email, alert_id):
    try:
        get_hotel_offer(email,alert_id)

    except PriceAlert.DoesNotExist:
        # Handle the case when there's no matching PriceAlert.
        # Maybe log an error or send a notification
        pass
    except Exception as e:
        # Handle any other exceptions that might occur.
        # Logging it is a good practice.
        pass

    return
    """