import base64
import json
from dotenv import load_dotenv
from datetime import datetime
from decimal import Decimal
import requests
from datashape import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.checks import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import path
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView
from oscar.apps.dashboard.communications.views import ListView

from .PriceAlert.models import PriceAlert
from .booking_platform import access_token_builder, hotel_auto_complete, get_hotel_offer_list, get_geocode, post_booking
from .coding import generate_key, encrypt_card, decrypt_card
from .models import Product
from .order.models import Order
from .product import HandleHotel, create_new_category
from offer_holding.models import OfferInformation
import os

load_dotenv()

AMADEUS_API_KEY = os.getenv('AMADEUS_API_KEY')
AMADEUS_API_SECRET = os.getenv('AMADEUS_API_SECRET')
CREDIT_CARD_KEY = os.getenv('CREDIT_CARD_KEY')
SEARCH_LOCATION_KEY = os.getenv('SEARCH_LOCATION_KEY')
USERNAME = None

"""
Adds a product to the basket and redirects to the checkout page.

@param request: The HTTP request object.
@param product_id: The ID of the product to add to the basket.
@return: A redirection to the checkout page.
"""


@login_required
def add_to_basket_and_checkout(request, product_id):
    # Get the product
    product = Product.objects.get(id=product_id)
    # Get the basket
    basket = request.basket

    basket.flush()
    # Add the product to the basket
    basket.add_product(product)
    # Redirect to the checkout page
    return redirect('checkout:index')  # replace 'checkout:index' with your actual checkout URL name


"""
Custom login view.
@redirect_authenticated_user: Flag to redirect authenticated users.
"""


class MyLoginView(LoginView):
    redirect_authenticated_user = True
    """
     Validates the login form.

     @param form: The login form.
     @return: A redirection to the next URL if present, otherwise the default behavior.
     """

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')

        if not remember_me:
            self.request.session.set_expiry(0)

        next_url = self.request.GET.get('next')
        if next_url:
            return redirect(next_url)

        return super().form_valid(form)


"""
Adds a parent product to the database.
@param title: The title of the parent product.
@param description: The description of the parent product.
@param category: The category of the parent product.
@param partner: The partner of the parent product (default is "Default Partner").
@return: The added parent product.
"""

handel = HandleHotel()
# handel.remove_hotels(offer_id=None)

access_token = access_token_builder(api_key=AMADEUS_API_KEY, api_secret=AMADEUS_API_SECRET)

"""
Renders the book page.
@param request: The HTTP request object.
@param offer_id: The ID of the offer.
@param hotel_name: The name of the hotel.
@param price: The price of the booking.
@return: The rendered book page.
"""


@login_required(login_url='/accounts/login/')
@require_http_methods(["GET"])
def book(request, offer_id, hotel_name, price):
    # price = float(price) * float(request.session["roomQuantity"])
    request.session['offer_id'] = offer_id
    return render(request, 'checkout/payment-details/',
                  {'offer_id': offer_id, 'hotel_name': hotel_name, 'price': price})


def delete_offerId(username):
    # Delete any existing records with this offer_id
    OfferInformation.objects.filter(username=username).delete()


"""
Handles the payment form submission.
@param request: The HTTP request object.
@return: A redirection to the preview page or the previous page if there are errors.
"""


@login_required(login_url='/accounts/login/')
@require_POST
def handle_payment(request):
    # Extract all the form data from the POST request
    key = CREDIT_CARD_KEY.encode()
    offer_id = [line.product.title for line in request.basket.lines.all()][0].split(",")[0]
    username = get_username(request=request)
    delete_offerId(username=username)
    title = request.POST.get('title', '')
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')
    phone = request.POST.get('phone', '')
    email = request.POST.get('email', '')
    payment_method = request.POST.get('method', '')
    card_vendor_code = request.POST.get('vendor_code', '')
    encrypted_card = encrypt_card(key, request.POST.get('card_number', ''))
    card_number = encrypted_card
    card_expiry_date = request.POST.get('expiry_date', '')

    # Validate that none of the fields are empty
    if not all([title, first_name, last_name, phone, email, payment_method, card_vendor_code, card_number,
                card_expiry_date]):
        # One or more fields are empty. We will not process the form
        messages.error(request, "Please fill all the fields.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Save all the form data to the new model
    offer_information = OfferInformation(
        username=username,
        offer_id=offer_id,
        title=title,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        payment_method=payment_method,
        card_vendor_code=card_vendor_code,
        card_number=encrypted_card,  # Remember to encrypt this in the actual model
        card_expiry_date=card_expiry_date  # Remember to encrypt this in the actual model
    )
    offer_information.save()
    basket = request.basket

    context = {
        'offer_info': offer_information,
        'basket': basket,
        # ... any other context you might want to pass
    }
    # Now that the data is saved, you can proceed with your logic
    return render(request, 'oscar/checkout/preview.html', context)


@login_required(login_url='/accounts/login/')
def checkout_preview(request):
    username = get_username(request=request)

    try:
        offer_info = OfferInformation.objects.get(username=username)
    except OfferInformation.DoesNotExist:
        offer_info = None

    context = {
        'offer_info': offer_info,
    }

    return render(request, 'checkout:preview', context)


"""
Removes payment-related session data.
@param request: The HTTP request object.
"""


def remove_handle_payment(request):
    keys_to_remove = ['title', 'first_name', 'last_name', 'phone', 'email', 'payment_method',
                      'card_vendor_code', 'card_number', 'card_expiry_date']

    for key in keys_to_remove:
        if key in request.session:
            del request.session[key]


"""
Renders the home page.
@param request: The HTTP request object.
@return: The rendered home page.
"""


def home(request):
    return render(request, 'index.html')


"""
View for payment details.
Inherits from CorePaymentDetailsView.

handle_successful_order: Handles a successful order.

Additional session data: booking_id, provider_confirmation_id, reference_id, origin_system_code.
"""


class PaymentDetailsView(CorePaymentDetailsView):
    def handle_successful_order(self, order):
        booking_id = self.request.session.get('booking_id')
        provider_confirmation_id = self.request.session.get('provider_confirmation_id')
        reference_id = self.request.session.get('reference_id')
        origin_system_code = self.request.session.get('origin_system_code')

        if booking_id:
            order.booking_id = booking_id
        if provider_confirmation_id:
            order.provider_confirmation_id = provider_confirmation_id
        if reference_id:
            order.reference_id = reference_id
        if origin_system_code:
            order.origin_system_code = origin_system_code

        order.save()

        super().handle_successful_order(order)


from django.contrib import messages  # Import the messages framework
from django.http import HttpResponseRedirect, HttpResponse
from oscar.core.loading import get_class

# from frobshop.offer_holding.models import OfferInformation

OrderTotalCalculator = get_class('checkout.calculators', 'OrderTotalCalculator')

"""
Handles the completion of a purchase.
@ param request The HTTP request object which contains session data and basket data.
@ returns A JSON response containing the booking id, provider confirmation id, reference id, and origin system code.
"""


@require_http_methods(["POST"])
def complete_purchase(request):
    offer_id = [line.product.title for line in request.basket.lines.all()][0].split(",")[0]

    # Fetch the data using the offer_id from the OfferInformation model
    try:
        offer_info = OfferInformation.objects.get(offer_id=offer_id)
    except OfferInformation.DoesNotExist:
        # Handle the case where the data does not exist
        return JsonResponse({'status': 'error', 'message': 'Offer information not found.'}, status=404)
    key = CREDIT_CARD_KEY.encode()
    # Extract data from the queried object
    title = offer_info.title
    first_name = offer_info.first_name
    last_name = offer_info.last_name
    phone = offer_info.phone
    email = offer_info.email
    payment_method = offer_info.payment_method
    card_vendor_code = offer_info.card_vendor_code
    card_encrypt = offer_info.card_number
    card_number = decrypt_card(key, card_encrypt)
    card_expiry_date = offer_info.card_expiry_date
    booking_response = post_booking(access_token=access_token, offer_id=offer_id, title=title, first_name=first_name,
                                    last_name=last_name,
                                    phone=phone, email=email, method="CreditCard", vendor_code=card_vendor_code,
                                    card_number=card_number, expiry_date=card_expiry_date)
    if booking_response is not None:

        booking_id = booking_response['data'][0]['id']
        provider_confirmation_id = booking_response['data'][0]['providerConfirmationId']
        reference_id = booking_response['data'][0]['associatedRecords'][0]['reference']
        origin_system_code = booking_response['data'][0]['associatedRecords'][0]['originSystemCode']

        # Save the new fields in the session
        request.session['booking_id'] = booking_id
        request.session['provider_confirmation_id'] = provider_confirmation_id
        request.session['reference_id'] = reference_id
        request.session['origin_system_code'] = origin_system_code
        return JsonResponse({
            'status': 'success',
            'booking_id': booking_id,
            'provider_confirmation_id': provider_confirmation_id,
            'reference_id': reference_id,
            'origin_system_code': origin_system_code,
        })


"""
    * Adds new elements to an existing order.
    * 
    * @param request          The HTTP request object which contains session data.
    * @param order_number     The unique identifier of the order to which new elements are added.
    *
    * @returns Nothing. The function saves the changes to the Order model.
"""


def add_new_elements_to_order(request, order_number):
    order = Order.objects.get(number=order_number)
    order.Booking_ID = request.session['booking_id']
    order.Provider_Confirmation_ID = request.session['provider_confirmation_id']
    order.Reference_ID = request.session['reference_id']
    order.Origin_System_Cod = request.session['origin_system_code']
    order.save()

    context = {
        'order': order,
        # ... other context variables ...
    }


from django.views import View

"""
* Class-based view to add new elements to an existing order.
* Uses the HTTP POST method.
*
* @param request          The HTTP request object, expecting 'order_number' in POST data.
* 
* @returns A JSON response with status 'ok'.
"""


class AddElementsToOrderView(View):
    def post(self, request):
        order_number = request.POST.get('order_number')
        add_new_elements_to_order(request, order_number)
        return JsonResponse({'status': 'ok'})


"""
* Handles the confirmation of an order.
*
* @param request          The HTTP request object containing form data and offer_id in the session.
*
* @returns A rendered template '/checkout/thank-you/' with booking data context.
"""


@require_http_methods(["POST"])
def confirm(request):
    booking_response = None
    # Get form data
    if request.method == 'POST':
        title = request.POST.get('title')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        method = request.POST.get('method')
        vendor_code = request.POST.get('vendor_code')
        card_number = request.POST.get('card_number')
        expiry_date = request.POST.get('expiry_date')
        # Get offer_id from the session
        offer_id = request.session.get('offer_id')

        # Post booking
        booking_response = post_booking(access_token=access_token, offer_id=offer_id, title=title,
                                        first_name=first_name, last_name=last_name,
                                        phone=phone, email=email, method=method, vendor_code=vendor_code,
                                        card_number=card_number, expiry_date=expiry_date)

    return render(request, '/checkout/thank-you/', {'booking_data': booking_response})


"""
* Retrieves the username of the currently authenticated user.
*
* @param request          The HTTP request object containing user data.
*
* @returns The username of the authenticated user, or None if the user is not authenticated.
"""


def get_username(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.email
    return username


"""
* Retrieves a list of hotel offers based on search criteria.
*
* @param request          The HTTP request object containing search criteria data in POST.
*
* @returns A redirect to a catalogue page with the hotel offers.
"""


@require_http_methods(["POST"])
def get_hotel_offers(request):
    # cityCode = request.form['cityCode']
    checkInDate = request.POST['checkInDate']
    checkOutDate = request.POST['checkOutDate']
    adults = request.POST['adults']
    roomQuantity = request.POST['roomQuantity']
    request.session["roomQuantity"] = roomQuantity
    location = request.POST['location']
    lat, lng = get_geocode(location)
    username = get_username(request=request)
    category = create_new_category(username)
    request.session['location'] = location
    handel.remove_hotels(offer_id=None, category=category)
    hotel_offers = get_hotel_offer_list(access_token=access_token, username=username, lat=lat, lng=lng,
                                        checkInDate=checkInDate, category=category,
                                        checkOutDate=checkOutDate, adults=adults, roomQuantity=roomQuantity)
    user, domain = username.split('@')
    dom, dotdomain = domain.split('.')
    user = user + dom + dotdomain
    # products_less_than_5_stars = Product.objects.annotate(avg_rating=Avg('ratingproduct__rating')).filter(avg_rating__lt=5)

    return redirect(f'/catalogue/category/{user}_{category.id}/', hotel_offers)


"""
* Retrieves a hotel offer based on an alert.
*
* @param request          The HTTP request object.
* @param alert_id         The unique identifier of the PriceAlert object.
*
* @returns A redirect to a catalogue page with the hotel offers.
"""


@require_http_methods(["POST"])
def get_hotel_offer(request, alert_id):
    alert = PriceAlert.objects.get(pk=alert_id)
    lat = 0
    lng = 0
    checkInDate = alert.check_in_date
    checkOutDate = alert.check_out_date
    adults = alert.number_of_adults
    roomQuantity = alert.number_of_rooms
    username = get_username(request=request)
    category = create_new_category(username)
    hotel_id = alert.hotel_id
    handel.remove_hotels(offer_id=None, category=category)
    hotel_offers = get_hotel_offer_list(access_token=access_token, username=username, lat=lat, lng=lng,
                                        checkInDate=checkInDate, category=category,
                                        checkOutDate=checkOutDate, adults=adults, roomQuantity=roomQuantity,
                                        hotel_id=hotel_id)
    user, domain = username.split('@')
    dom, dotdomain = domain.split('.')
    user = user + dom + dotdomain
    return redirect(f'/catalogue/category/{user}_{category.id}/', hotel_offers)


import schedule
import time


# Mock request for testing
class SimulatedRequest:
    def __init__(self, user):
        self.user = user

    @staticmethod
    def get_username(request):
        return request.user


# Simulated request with a test username (adjust as needed)
simulated_request = SimulatedRequest(user="nivdoron1234@gmail.com")

# Assuming you have a model called PriceAlert, get the id of the first alert.
# This is just for testing purposes. Adjust as needed.
alert_id = PriceAlert.objects.get(email="nivdoron1234@gmail.com") if PriceAlert.objects.exists() else None

from datetime import datetime, timedelta

"""
* Handles the index view of the website.
*
* @param request          The HTTP request object.
*
* @returns A rendered index.html template with user context if the user is authenticated.
"""


@login_required(login_url='/accounts/login/')
@require_http_methods(["GET", "POST"])
def index(request):
    if request.user.is_authenticated:
        user_email = request.user.email
        username, domain = user_email.split('@')
        context = {
            'username': username,
        }
    else:
        context = {}
    return render(request, 'index.html', context)


"""
* Handles a geocode search based on a query.
*
* @param request          The HTTP request object containing the query in GET data.
*
* @returns A JSON response containing geocode search results.
"""


@require_http_methods(["GET"])
def search(request):
    search_query = request.GET.get('query', '')
    if len(search_query) >= 3:
        url = f'https://api.geoapify.com/v1/geocode/search?apiKey={SEARCH_LOCATION_KEY}&text={search_query}'
        response = requests.get(url)
        data = json.loads(response.text)
        if 'features' in data:
            data['features'] = data['features'][:5]
        else:
            data = {'features': []}
        return JsonResponse(data)  # return JSON response
    else:
        return JsonResponse({'features': []})  # return empty list if query is too short


"""
* Handles the hotels view of the website.
*
* @param request          The HTTP request object.
*
* @returns A rendered template for a category page.
"""


@require_http_methods(["GET"])
def hotels(request):
    username = get_username(request=request)
    user, domain = username.split('@')
    dom, dotdomain = domain.split('.')
    user = user + dom + dotdomain
    category = create_new_category(category_name=user)

    return render(request, f'/catalogue/category/{user}_{category.id}/')


from django.core import serializers
from django.http import JsonResponse
from django.views import View
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

"""
 This is a Django View class which processes a POST request and returns a list of products filtered by the provided
 ratings.

 :method post: Handles POST request.
 """


@method_decorator(csrf_exempt, name='dispatch')
class ProductFilterView(View):
    def post(self, request, *args, **kwargs):
        data = request.body.decode('utf-8')
        ratings = json.loads(data)
        q_objects = Q()
        for rating in ratings:
            q_objects |= Q(rating=rating)
        products = Product.objects.filter(q_objects, parent=None)  # only parent products
        serialized_products = serializers.serialize('json', products)
        return JsonResponse({'products': serialized_products}, status=200)


"""
This function filters a list of products based on the provided ratings. It fetches all products and then applies
filters on the rating attribute.

:param request: Django HttpRequest object.
:return: Rendered product list HTML page.
"""


def filter(request):
    products = Product.objects.all()

    # Filtering based on star rating
    ratings = request.GET.getlist('rating')
    if ratings:
        q_objects = Q()
        for rating in ratings:
            q_objects |= Q(productreview__score=rating)
        products = products.filter(q_objects)

    # Add other filters as necessary

    return render(request, 'product_list.html', {'products': products})


"""
This function handles the GET requests for hotel auto-complete functionality.

:param request: HttpRequest object, The request object from the client.
:return: JsonResponse containing a list of hotel suggestions.
"""


@require_http_methods(["GET"])
def hotel_search_auto_complete(request):
    search_query = request.GET.get('query', '')
    data_list = []
    if len(search_query) >= 3:
        data = hotel_auto_complete(name=search_query, access_token=access_token)
        for dat in data["data"]:
            if dat is not None:
                data_list.append(dat["name"] + "," + dat["hotelIds"][0])
    return JsonResponse({'features': data_list})


"""
This function handles the GET and POST requests for viewing a hotel.

:param request: HttpRequest object, The request object from the client.
:return: HttpResponse object, redirects to the price alert page if the request method is POST.
"""


@login_required(login_url='/accounts/login/')
@require_http_methods(["GET", "POST"])
def hotel_view(request):
    if request.method == 'POST':
        user_email = request.user.email
        hotel_name = request.POST.get('location')
        check_in_date = datetime.strptime(request.POST.get('checkInDate'), "%Y-%m-%d").date()
        check_out_date = datetime.strptime(request.POST.get('checkOutDate'), "%Y-%m-%d").date()
        number_of_adults = int(request.POST.get('adults'))
        number_of_rooms = int(request.POST.get('roomQuantity'))
        price = Decimal(request.POST.get('price'))
        hotel_id = request.POST.get('location').split(",")[-1]

        alert, created = PriceAlert.objects.get_or_create(
            user=request.user,
            email=user_email,
            hotel_name=hotel_name,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            number_of_adults=number_of_adults,
            number_of_rooms=number_of_rooms,
            price=price,
            hotel_id=hotel_id,
        )

        return HttpResponseRedirect('/accounts/alerts/')


"""
This function retrieves a list of price alerts for a logged-in user.

:param request: HttpRequest object, The request object from the client.
:return: HttpResponse object, renders a list of price alerts for the logged-in user.
"""


@login_required(login_url='/accounts/login/')
@require_http_methods(["GET", "POST"])
def alerts_list(request):
    alerts = PriceAlert.objects.filter(user=request.user)
    return render(request, 'oscar/customer/alerts/alert_list.html', {'alerts': alerts})


from oscar.apps.catalogue.models import Product

"""
This function sorts the child products of a given parent product by price.

:param parent_product: Product, The parent product whose child products need to be sorted.
:return: QuerySet, sorted list of child products by price.
"""


def sort_child_products_by_price(parent_product):
    # Retrieve all the child products for the given parent
    child_products = Product.objects.filter(parent=parent_product)

    # Sort the child products by their price
    sorted_child_products = child_products.order_by('stockrecords__price')
    return sorted_child_products


# URLs mapping

urlpatterns = [
    path('', index, name='index'),
    path('search', search, name='search'),
    path('hotel_search_auto_complete', hotel_search_auto_complete, name='hotel_search_auto_complete'),
    path('hotels', hotels, name='hotels'),
    path('get_hotel_offers', get_hotel_offers, name='get_hotel_offers'),
    path('book', book, name='book'),
    path('confirm', confirm, name='confirm'),
    path('hotel_view', hotel_view, name='hotel_view'),
    path('alerts_list', alerts_list, name='alerts_list'),
]
