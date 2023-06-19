import oscar.apps.checkout.calculators
from django.http import HttpResponseRedirect
from django.urls import reverse
from oscar.apps.checkout.views import ShippingAddressView as OscarShippingAddressView, \
    ShippingMethodView as OscarShippingMethodView, PaymentDetailsView as OscarPaymentDetailsView
oscar.apps.checkout.calculators
class ShippingAddressView(OscarShippingAddressView):
    def get(self, request, *args, **kwargs):
        self.checkout_session.ship_to_user_address(None)
        return HttpResponseRedirect(reverse('checkout:shipping-method'))


class ShippingMethodView(OscarShippingMethodView):
    def get(self, request, *args, **kwargs):
        self.checkout_session.use_shipping_method(None)
        return HttpResponseRedirect(reverse('checkout:payment-details'))


class PaymentDetailsView(OscarPaymentDetailsView):
    pass  # Keep this if you don't need any custom logic for the PaymentDetailsView.
