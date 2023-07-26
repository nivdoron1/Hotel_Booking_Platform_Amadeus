from django.core.mail import send_mail
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.core.management.base import BaseCommand

from frobshop.frobshop.PriceAlert.models import PriceAlert
from frobshop.frobshop.models import *  # Replace 'your_app' with the name of your Django app

class Command(BaseCommand):
    help = 'Notify users with check-in dates in the past'

    def handle(self, *args, **options):
        alerts_with_past_dates = PriceAlert.objects.filter(check_in_date__lt=now().date())
        for alert in alerts_with_past_dates:
            send_mail(
                'Your Check-in Date is in the Past',
                render_to_string(
                    'email_template.txt',  # update this with your email template
                    {
                        'name': alert.user.first_name,  # update these with your actual variables
                        'check_in_date': alert.check_in_date,
                    }
                ),
                'nivdoron1234@hotmail.com',  # your Oscar email here
                [alert.user.email],
                fail_silently=False,
            )
