from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from .PriceAlert.models import PriceAlert

"""
This function deletes a price alert with a given alert ID.

:param request: HttpRequest object, The request object from the client.
:param alert_id: int, The id of the alert to be deleted.
:return: HttpResponse object, redirects to the price alerts page after deleting the alert.
"""


def delete_alert(request, alert_id):
    alert = PriceAlert.objects.get(pk=alert_id)
    alert.delete()
    return redirect('price_alerts')


"""
This function retrieves a list of all price alerts.

:param request: HttpRequest object, The request object from the client.
:return: HttpResponse object, renders a list of all price alerts.
"""


def price_alerts(request):
    alerts = PriceAlert.objects.all()
    now = timezone.now().date()
    PriceAlert.objects.filter(check_in_date__lt=now).delete()
    return render(request, 'price_alerts.html', {'alerts': alerts})
