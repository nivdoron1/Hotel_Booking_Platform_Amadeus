from django.conf import settings
import paypalrestsdk
from django.urls import reverse
from paypalrestsdk import Order

# Setup PayPal client with your credentials
paypalrestsdk.configure({
    "mode": settings.PAYPAL_API_SANDBOX_MODE,  # sandbox or live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})


def fetch_order(order_id):
    """
    This function should interact with your database and fetch the order
    based on the order id. This is heavily dependent on your implementation,
    so this is just a simple example.
    """
    # Replace this with actual implementation
    order = Order.objects.get(id=order_id)
    return order


def handle_payment(order, request):
    """
    This function will interact with the PayPal SDK to create and process the payment.
    """
    # Create payment object
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('your-return-url')),
            "cancel_url": request.build_absolute_uri(reverse('your-cancel-url'))
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "item",
                    "sku": "item",
                    "price": str(order.total),  # Replace this with your order total
                    "currency": "USD",  # Replace this with your currency
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(order.total),  # Replace this with your order total
                "currency": "USD"  # Replace this with your currency
            },
            "description": "This is the payment description."
        }]
    })

    # Create Payment and return status
    if payment.create():
        print("Payment[%s] created successfully" % (payment.id))
        # Redirect the user to given approval url
        for link in payment.links:
            if link.method == "REDIRECT":
                redirect_url = str(link.href)
                return redirect_url
    else:
        print("Error while creating payment:")
        print(payment.error)
