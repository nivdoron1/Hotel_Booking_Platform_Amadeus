from datashape import Decimal
from django.core.checks import messages
from amadeus import amadeus
from django.http import JsonResponse, HttpResponseRedirect
import json
from django.utils import timezone
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import path
from django.views import View
from django.views.decorators.http import require_http_methods
from oscar.apps.customer.views import AccountRegistrationView as CoreAccountRegistrationView
from oscar.apps.partner.models import Partner, StockRecord
from oscar.apps.partner.strategy import Selector
from requests.auth import HTTPBasicAuth

from .models import Product
from .order.models import Order

# api_key = 'nc3HcfEOuEoLQ8tKgGmXemwP8XkfDKbs'
# api_secret = 'slE8rqApxZBdXCU5'
api_key = '8vZfCYy8QB53BCZpmAr05cVnIUDFiFoI'
api_secret = 'FbeNpLvRVzY25yW2'
USERNAME = None
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from oscar.apps.catalogue.models import Product, ProductImage, Category

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
Builds an access token for the API.
@param api_key: The API key.
@param api_secret: The API secret.
@return: The access token.
"""


def access_token_builder(api_key, api_secret):
    url = "https://api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials"
    }
    access_token = None
    response = requests.post(url, auth=HTTPBasicAuth(api_key, api_secret), data=payload)
    access_token = None
    if response.status_code == 200:
        access_token = response.json()["access_token"]
    else:
        print("Error:", response.status_code, response.text)
    return access_token


from oscar.apps.partner.models import Partner
from oscar.apps.catalogue.models import ProductCategory
import locale
from oscar.apps.catalogue.categories import create_from_breadcrumbs


class HandleHotel:
    """
    Constructor for the HandleHotel class.
    """

    def __init__(self):
        self.hotels_list = {}
        #self.remove_hotels(offer_id=None)

    """
    Removes hotels from the database.

    @param offer_id: The ID of the offer to remove. If None, removes all hotels.
    """

    def remove_hotels(self, offer_id,category):
        if offer_id is None:

            # Get all products in the 'hello' category
            products_in_category = Product.objects.filter(categories__in=[category])

            # Delete all these products
            products_in_category.delete()
        elif self.hotels_list is {}:
            return ""
        else:
            # Get the product corresponding to the offer_id
            product = Product.objects.get(title=offer_id)
            # Get the hotel ID of this product
            product_hotel = product.parent.title

            # Get all parent (hotel) products
            parent_products = Product.objects.filter(structure=Product.PARENT)

            for parent_product in parent_products:
                if parent_product.title in self.hotels_list:
                    # If the hotel is in hotels_remove, get all its child products (offers)
                    child_products = Product.objects.filter(parent=parent_product)
                    for child_product in child_products:
                        # If the offer is not in the list for this hotel in hotels_remove, delete it
                        if child_product.title not in self.hotels_list[parent_product.title]:
                            delete_child_product(title=child_product.title, parent_title=parent_product.title)
                else:
                    # If the hotel is not in hotels_remove, delete it
                    delete_parent_product(title=parent_product.title)
        self.hotels_list = {}


"""
Deletes a child product from the database.
@param title: The title of the child product.
@param parent_title: The title of the parent product.
"""


def delete_child_product(title, parent_title):
    try:
        parent_product = Product.objects.get(title=parent_title, structure=Product.PARENT)
        child_product = Product.objects.get(title=title, parent=parent_product)
        child_product.delete()
        print(f"Deleted child product with title {title} under parent product {parent_title}")
    except Product.DoesNotExist:
        print(f"Child product with title {title} under parent product {parent_title} does not exist")


"""
Deletes a parent product from the database.
@param title: The title of the parent product.
"""


def delete_parent_product(title):
    try:
        product = Product.objects.get(title=title, structure=Product.PARENT)
        product.delete()
        print(f"Deleted parent product with title {title}")
    except Product.DoesNotExist:
        print(f"Parent product with title {title} does not exist")


"""
Adds a child product to the database.
@param title: The title of the child product.
@param description: The description of the child product.
@param parent_product: The parent product.
@param currency: The currency of the child product's price.
@param price: The price of the child product.
@param partner: The partner of the child product (default is "Default Partner").
@return: The added child product.
"""


def add_child_product(title, description, parent_product, currency, price, partner="Default Partner"):
    # Check if the child product already exists
    partner, created = Partner.objects.get_or_create(name=partner)
    child_product = None
    if not Product.objects.filter(title=title, parent=parent_product).exists():
        child_product = Product.objects.create(
            title=title,
            description=description,
            parent=parent_product,
            structure=Product.CHILD
        )

        # Generate SKU from the product title
        sku = title.replace(" ", "_").upper()

        # Create a stock record for the child product
        stock_record = StockRecord.objects.create(
            product=child_product,
            partner=partner,
            partner_sku=sku,  # Replace with your unique SKU
            price_currency=currency,  # Replace with your preferred currency
            price=price,  # Replace with your price
            num_in_stock=1,  # Replace with your stock quantity
            num_allocated=0,  # Replace with your allocated stock quantity
            low_stock_threshold=1,  # Replace with your low stock threshold
        )
        stock_record.save()
        # Fetch the price and availability using the strategy framework
        strategy = Selector().strategy(request=None, user=None)
        info = strategy.fetch_for_product(child_product)
    else:
        child_product = Product.objects.get(title=title, parent=parent_product)
    return child_product


"""
Adds a parent product to the database.
@param title: The title of the parent product.
@param description: The description of the parent product.
@param category: The category of the parent product.
@param partner: The partner of the parent product (default is "Default Partner").
@return: The added parent product.
"""

import io
from django.core.files.base import ContentFile
from PIL import Image

from django.core.files.base import ContentFile
from oscar.core.loading import get_model
from PIL import Image
import io

Product = get_model('catalogue', 'product')
ProductImage = get_model('catalogue', 'ProductImage')

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from oscar.apps.catalogue.models import ProductImage


def add_image_to_product(product, image_binary):
    # Check if the product exists
    if not isinstance(product, Product):
        raise ValueError("The product parameter should be an instance of Product model")

    # Create a ContentFile object from binary data
    image_content = ContentFile(image_binary)

    # Create InMemoryUploadedFile from ContentFile
    uploaded_image = InMemoryUploadedFile(image_content, None, 'image.jpg', 'image/jpeg', image_content.tell, None)

    # Create a new ProductImage object and associate it with the product
    product_image = ProductImage.objects.create(product=product, original=uploaded_image)

    return product_image


def add_parent_product(title, description, category, image_data, partner="Default Partner"):
    partner, created = Partner.objects.get_or_create(name=partner)
    print(f"Partner: {partner}, Created: {created}")
    parent_product = None
    # Check if the parent product already exists
    if not Product.objects.filter(title=title).exists():
        # Create the parent product
        parent_product = Product.objects.create(title=title,
                                                description=description,
                                                product_class_id=3,
                                                structure=Product.PARENT)  # Use appropriate product class id

        product_category = ProductCategory.objects.create(product=parent_product, category=category)
        add_image_to_product(product=parent_product, image_binary=image_data)
    else:
        parent_product = Product.objects.get(title=title)
        print(f"Found existing product: {parent_product}")

    return parent_product


handel = HandleHotel()
#handel.remove_hotels(offer_id=None)

access_token = access_token_builder(api_key=api_key, api_secret=api_secret)

"""
Creates a new category.
@param category_name: The name of the category.
@return: The created category.
"""


def create_new_category(category_name):
    return create_from_breadcrumbs(category_name)


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


from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

"""
Handles the payment form submission.
@param request: The HTTP request object.
@return: A redirection to the preview page or the previous page if there are errors.
"""


@login_required(login_url='/accounts/login/')
@require_POST
def handle_payment(request):
    # Extract all the form data from the POST request
    offer_id = [line.product.title for line in request.basket.lines.all()][0].split(",")[0]
    print(offer_id)
    title = request.POST.get('title', '')
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')
    phone = request.POST.get('phone', '')
    email = request.POST.get('email', '')
    payment_method = request.POST.get('method', '')
    card_vendor_code = request.POST.get('vendor_code', '')
    card_number = request.POST.get('card_number', '')
    card_expiry_date = request.POST.get('expiry_date', '')

    # Validate that none of the fields are empty
    if not all([title, first_name, last_name, phone, email, payment_method, card_vendor_code, card_number,
                card_expiry_date]):
        # One or more fields are empty. We will not process the form
        messages.error(request, "Please fill all the fields.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Save all the form data to the session
    request.session['title'] = title
    request.session['first_name'] = first_name
    request.session['last_name'] = last_name
    request.session['phone'] = phone
    request.session['email'] = email
    request.session['payment_method'] = payment_method
    request.session['card_vendor_code'] = card_vendor_code
    request.session['card_number'] = card_number
    request.session['card_expiry_date'] = card_expiry_date
    # Redirect to the '/checkout/preview/' page
    return redirect('checkout:preview')


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


from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView

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
from django.http import HttpResponseRedirect
from oscar.apps.partner.strategy import Selector
from oscar.core.loading import get_class

OrderTotalCalculator = get_class('checkout.calculators', 'OrderTotalCalculator')

"""
Handles the completion of a purchase.
@ param request The HTTP request object which contains session data and basket data.
@ returns A JSON response containing the booking id, provider confirmation id, reference id, and origin system code.
"""


@require_http_methods(["POST"])
def complete_purchase(request):
    offer_id = [line.product.title for line in request.basket.lines.all()][0].split(",")[0]
    print(offer_id)
    title = request.session['title']
    first_name = request.session['first_name']
    last_name = request.session['last_name']
    phone = request.session['phone']
    email = request.session['email']
    payment_method = request.session['payment_method']
    card_vendor_code = request.session['card_vendor_code']
    card_number = request.session['card_number']
    card_expiry_date = request.session['card_expiry_date']
    print(len(offer_id))
    booking_response = post_booking(offer_id=offer_id, title=title, first_name=first_name, last_name=last_name,
                                    phone=phone, email=email, method="CreditCard", vendor_code=card_vendor_code,
                                    card_number=card_number, expiry_date=card_expiry_date)
    print(booking_response)
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
        booking_response = post_booking(offer_id=offer_id, title=title, first_name=first_name, last_name=last_name,
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
    handel.remove_hotels(offer_id=None,category=category)
    hotel_offers = get_hotel_offer_list(username=username,lat=lat, lng=lng, checkInDate=checkInDate, category=category,
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
    handel.remove_hotels(offer_id=None,category=category)
    hotel_offers = get_hotel_offer_list(username=username,lat=lat, lng=lng, checkInDate=checkInDate, category=category,
                                        checkOutDate=checkOutDate, adults=adults, roomQuantity=roomQuantity,
                                        hotel_id=hotel_id)
    user, domain = username.split('@')
    dom, dotdomain = domain.split('.')
    user = user + dom + dotdomain
    return redirect(f'/catalogue/category/{user}_{category.id}/', hotel_offers)


from oscar.apps.catalogue.views import ProductCategoryView

"""
* A custom class-based view to display a list of products in a category, excluding 5-star products.
*
* @returns A queryset of products that is displayed in the view.
"""


class CustomProductCategoryView(ProductCategoryView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(avg_rating=Avg('reviews__rating')).exclude(avg_rating=5)


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
        api_key = "eae94a3f14c04f68995683196c596285"
        url = f'https://api.geoapify.com/v1/geocode/search?apiKey={api_key}&text={search_query}'
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


"""
This function fetches a list of hotels in a specific city. It calls the Amadeus API and returns a list of hotels
based on the provided city code.

:param cityCode: str, The code of the city to fetch hotels.
:return: json response containing hotels data.
"""


def get_hotel_city_list(cityCode):
    url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    params = {
        "cityCode": cityCode,
        "radius": 5,
        "ratings": "2,3,4,5",
        "amenities": "SWIMMING_POOL,SPA,FITNESS_CENTER,AIR_CONDITIONING,RESTAURANT,PARKING,PETS_ALLOWED,"
                     "AIRPORT_SHUTTLE,BUSINESS_CENTER,DISABLED_FACILITIES,WIFI,MEETING_ROOMS,NO_KID_ALLOWED,TENNIS,"
                     "GOLF,KITCHEN,ANIMAL_WATCHING,BABY-SITTING,BEACH,CASINO,JACUZZI,SAUNA,SOLARIUM,MASSAGE,"
                     "VALET_PARKING,BAR%20or%20LOUNGE,KIDS_WELCOME,NO_PORN_FILMS,MINIBAR,TELEVISION,WI-FI_IN_ROOM,"
                     "ROOM_SERVICE,GUARDED_PARKG,SERV_SPEC_MENU",
        "radiusUnit": "KM",
        "hotelSource": "ALL",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            for hotel in data['data']:
                print('Hotel name:', hotel['name'])
                if 'rating' in hotel:
                    print('Rating:', hotel['rating'])
                else:
                    print('Rating: Not available')
        return response.json()
    else:
        print("Failed to get data:", response.status_code)


"""
This function returns the geocodes (latitude and longitude) of a specific location using the OpenCageData API.

:param location: str, The name of the location to fetch geocodes.
:return: Tuple containing latitude and longitude.
"""


def get_geocode(location):
    # OpenCageData API endpoint
    url = "https://api.opencagedata.com/geocode/v1/json"

    # Your OpenCageData API key (replace with your actual key)
    geo_api_key = "2fecee560d45478a804429353e15f715"

    # Parameters for the API request
    params = {
        'key': geo_api_key,
        'q': location,
        'limit': 1
    }

    # Send the GET request
    response = requests.get(url, params=params)

    # If the request was successful, return the latitude and longitude
    if response.status_code == 200:
        results = response.json()['results']
        if len(results) > 0:
            geometry = results[0]['geometry']
            return geometry['lat'], geometry['lng']

    # If the request failed, print the status code and return None
    print('Failed to get geocode: status code', response.status_code)
    return None


"""
This function fetches a list of hotels based on a geocode (latitude and longitude). It calls the Amadeus API
and returns a list of hotels.

:param latitude: float, The latitude of the location.
:param longitude: float, The longitude of the location.
:return: json response containing hotels data.
"""


def get_hotel_geo_list(latitude, longitude):
    url = "https://api.amadeus.com/v1/reference-data/locations/hotels/by-geocode"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": 5,
        "radiusUnit": "KM",
        "ratings": "2,3,4,5",
        "amenities": "SWIMMING_POOL,SPA,FITNESS_CENTER,AIR_CONDITIONING,RESTAURANT,PARKING,PETS_ALLOWED,"
                     "AIRPORT_SHUTTLE,BUSINESS_CENTER,DISABLED_FACILITIES,WIFI,MEETING_ROOMS,NO_KID_ALLOWED,TENNIS,"
                     "GOLF,KITCHEN,ANIMAL_WATCHING,BABY-SITTING,BEACH,CASINO,JACUZZI,SAUNA,SOLARIUM,MASSAGE,"
                     "VALET_PARKING,BAR%20or%20LOUNGE,KIDS_WELCOME,NO_PORN_FILMS,MINIBAR,TELEVISION,WI-FI_IN_ROOM,"
                     "ROOM_SERVICE,GUARDED_PARKG,SERV_SPEC_MENU",
        "hotelSource": "ALL",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to get data:", response.status_code)


from django.core import serializers
from django.http import JsonResponse
from django.views import View
from django.db.models import Q, Avg
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
This function fetches a list of hotel offers based on certain parameters like location, date, adults count etc. 
It calls the Amadeus API and returns a list of hotel offers.

:param lat: float, Latitude of the location.
:param lng: float, Longitude of the location.
:param category: str, The category of the hotel.
:param checkInDate: str, Check-in date in the format 'YYYY-MM-DD'.
:param checkOutDate: str, Check-out date in the format 'YYYY-MM-DD'.
:param adults: int, Number of adults.
:param roomQuantity: int, Number of rooms required.
:param paymentPolicy: str, Payment policy.
:param bestRateOnly: str, Flag to determine if only the best rate should be considered.
:param hotel_id: str, The id of the hotel. If none, fetch all hotels.
:return: json response containing hotel offers data.
"""


def get_hotel_offer_list(username,lat, lng, category, checkInDate, checkOutDate, adults, roomQuantity, paymentPolicy="NONE",
                         bestRateOnly="false", hotel_id=None):
    url = "https://api.amadeus.com/v3/shopping/hotel-offers"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    hotel_ids = []
    hotel_ids_d = []
    if hotel_id is not None:
        hotel_ids.append(hotel_id)
    else:
        hotel_ids_data = get_hotel_geo_list(latitude=lat, longitude=lng)
        print(hotel_ids_data)
        hotel_id = [d["hotelId"] for d in hotel_ids_data["data"]]
        for i in range(0, min(len(hotel_id), 5)):
            hotel_ids_d.append(hotel_ids_data["data"][i])
            hotel_ids.append(hotel_id[i])
    params = {
        "hotelIds": hotel_ids,
        "adults": adults,
        "checkInDate": checkInDate,
        "checkOutDate": checkOutDate,
        "roomQuantity": roomQuantity,
        "paymentPolicy": paymentPolicy,
        "bestRateOnly": bestRateOnly,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        hotel_details_list = []
        data = response.json()
        for item in data['data']:
            hotel_id = item['hotel']['name']
            hotel_hotelID = item['hotel']['hotelId']
            hotel_desc = {}
            for hotel_of in hotel_ids_d:
                if hotel_of.get('hotelId', '') == hotel_hotelID:
                    hotel_desc = hotel_of
                    break
            print(hotel_desc)
            hotel_stars = hotel_desc.get('rating', 0)
            handel.hotels_list[hotel_id] = []
            hotel_details = {
                'name': hotel_desc.get('name', ''),
                'hotelId': hotel_desc.get('hotelId', ''),
                'cityCode': item['hotel']['cityCode'],
                'chainCode': hotel_desc.get('chainCode', ''),
                'iataCode': hotel_desc.get('iataCode', ''),
                'dupeId': hotel_desc.get('dupeId', ''),
                'geoCode': "latitude: " + str(
                    hotel_desc.get('geoCode', {}).get('latitude', '')) + " longitude: " + str(
                    hotel_desc.get('geoCode', {}).get('longitude', '')),
                'address': hotel_desc.get('address', {}).get('countryCode', ''),
                'distance': str(hotel_desc.get('distance', {}).get('value', '')) + str(
                    hotel_desc.get('distance', {}).get('unit', '')) + " from location",
                'amenities': ' , '.join(hotel_desc.get('amenities', '')),
                'rating': hotel_desc.get('rating', ''),
                # 'giataId': hotel_ids_d[0]['giataId'] if hotel_ids_d != [] else "None",
                'lastUpdate': hotel_desc.get('lastUpdate', ''),
            }
            parent_description = json.dumps(hotel_details, indent=4)
            # print(parent_description)
            image = images_of_hotel(hotel_desc)

            parent_product = add_parent_product(title=username+","+hotel_id, description=parent_description, image_data=image,
                                                category=category)
            update_product_review_score(parent_product, hotel_stars)
            childs_list = []
            for offer in item['offers']:
                offer_id = offer['id']
                offer_name = offer_id + "," + offer.get('room', {}).get('typeEstimated', {}).get('category', "")
                handel.hotels_list[hotel_id].append(offer_id)
                price_changes = offer.get('price', {}).get('variations', {}).get('changes', [{}])[0]
                taxes = offer.get('price', {}).get('taxes', [])
                taxes_info = []
                for tax in taxes:
                    tax_info = {
                        'price taxes code': tax.get('code', ""),
                        'price taxes pricingFrequency': tax.get('pricingFrequency', ""),
                        'price taxes pricingMode': tax.get('pricingMode', ""),
                        'price taxes amount': tax.get('amount', ""),
                        'price taxes currency': tax.get('currency', ""),
                        'price taxes included': tax.get('included', ""),
                    }
                    taxes_info.append(tax_info)
                hotel_data = {
                    'checkInDate': offer.get('checkInDate', ""),
                    'checkOutDate': offer.get('checkOutDate', ""),
                    'rateCode': offer.get('rateCode', ""),
                    'room type': offer.get('room', {}).get('type', ""),
                    'room type category': offer.get('room', {}).get('typeEstimated', {}).get('category', ""),
                    'room type beds': offer.get('room', {}).get('typeEstimated', {}).get('beds', ""),
                    'room type bedType': offer.get('room', {}).get('typeEstimated', {}).get('bedType', ""),
                    'room lang': offer.get('room', {}).get('description', {}).get('lang', ""),
                    'room description': offer.get('room', {}).get('description', {}).get('text', ""),
                    'adults': offer.get('guests', {}).get('adults', ""),
                    'price currency': offer.get('price', {}).get('currency', ""),
                    'price total': offer.get('price', {}).get('total', ""),
                    'price taxes': offer.get('price', {}).get('taxes', ""),
                    'cancellations': offer.get('policies', {}).get('cancellations', ""),
                    'price changes startDate': price_changes.get('startDate', ""),
                    'price changes endDate': price_changes.get('endDate', ""),
                    'price changes total': price_changes.get('total', ""),
                    'changes': offer.get('changes', ""),
                    'price': offer.get('price', ""),
                    'guarantee': offer.get('policies', {}).get('guarantee', {}).get('acceptedPayments', {}).get(
                        'creditCards', ""),
                    'paymentType': offer.get('paymentType', ""),
                    # 'price taxes code': taxes_info[0]['price taxes code'],
                    # 'price taxes pricingFrequency': taxes_info[0]['price taxes pricingFrequency'],
                    # 'price taxes pricingMode': taxes_info[0]['price taxes pricingMode'],
                    # 'price taxes amount': taxes_info[0]['price taxes amount'],
                    # 'price taxes currency': taxes_info[0]['price taxes currency'],
                    # 'price taxes included': taxes_info[0]['price taxes included'],
                }
                hotel_description = json.dumps(hotel_data, indent=4)  # Convert the hotel data to a JSON string
                currency = hotel_data['price']['currency'] if hotel_data.get(
                    'price') else None
                total_price = locale.atof(hotel_data['price']['total']) * float(roomQuantity) if hotel_data.get(
                    'price') else 0
                data = {
                    'parent_product': parent_product,
                    'hotel_description': hotel_description,
                    'total_price': total_price,
                    'currency': currency,
                    'offer_name': offer_name,
                }
                childs_list.append(data)
            childs_list = sorted(childs_list, key=lambda k: k['total_price'], reverse=True)
            for child in childs_list:
                add_child_product(parent_product=child['parent_product'], description=child['hotel_description'],
                                  price=child['total_price'], currency=child['currency'], title=child['offer_name'])
        return data
    else:
        print("Failed to get data:", response.status_code)


"""
This function posts a booking using the Amadeus API. It takes various parameters like customer details, payment 
details etc. and returns a response from the API.

:param offer_id: str, The id of the offer.
:param title: str, Title of the guest.
:param first_name: str, First name of the guest.
:param last_name: str, Last name of the guest.
:param phone: str, Phone number of the guest.
:param email: str, Email of the guest.
:param method: str, Payment method.
:param vendor_code: str, Vendor code of the payment card.
:param card_number: str, Card number of the payment card.
:param expiry_date: str, Expiry date of the payment card in the format 'YYYY-MM'.
:return: json response containing booking data.
"""


def post_booking(offer_id, title, first_name, last_name, phone, email, method, vendor_code, card_number, expiry_date):
    url = "https://api.amadeus.com/v1/booking/hotel-bookings"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "data": {
            "offerId": offer_id,
            "guests": [
                {
                    "name": {
                        "title": title,
                        "firstName": first_name,
                        "lastName": last_name
                    },
                    "contact": {
                        "phone": phone,
                        "email": email
                    }
                }
            ],
            "payments": [
                {
                    "method": method,
                    "card": {
                        "vendorCode": vendor_code,
                        "cardNumber": card_number,
                        "expiryDate": expiry_date
                    }
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200 or response.status_code == 201:
        # handel.remove_hotels(offer_id=offer_id)
        return response.json()
    else:
        print("Failed to post booking:", response.status_code, response.text)
        return None


"""
This function uses the Amadeus API to get a list of hotel suggestions based on the input keyword.

:param name: str, the keyword used to search for hotels.
:return: json response containing hotel data or an error message if the request fails.
"""


def hotel_auto_complete(name):
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    url = 'https://api.amadeus.com/v1/reference-data/locations/hotel'
    params = {
        "keyword": name,
        "subType": 'HOTEL_GDS',
        "max": 5,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()

    return print(f"Failed to hotel_auto_complete: {response.status_code}, {response.text}")


from oscar.apps.catalogue.reviews.models import ProductReview

"""
This function updates the review score of a given product.

:param product: Product, The product whose review score needs to be updated.
:param new_score: float, The new review score.
:return: None
"""


def update_product_review_score(product, new_score):
    # Get the reviews of the product
    reviews = ProductReview.objects.filter(product=product)
    product.rating = new_score
    product.save()


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
        data = hotel_auto_complete(search_query)
        for dat in data["data"]:
            if dat is not None:
                data_list.append(dat["name"] + "," + dat["hotelIds"][0])
    return JsonResponse({'features': data_list})


from django.shortcuts import redirect
from datetime import datetime
from decimal import Decimal
from .PriceAlert.models import PriceAlert

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


import requests
import base64
from hotels.models import Hotel
from hotels.models import Image as Img
from PIL import Image, UnidentifiedImageError
from io import BytesIO


def images_of_hotel(hotel_detail):
    api_key = "AIzaSyCsIQGnoKbY33Q36J4fpJWzrOVcKjKVBZk"
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    lat = hotel_detail["geoCode"]["latitude"]
    lng = hotel_detail["geoCode"]["longitude"]
    coord = str(lat) + "," + str(lng)
    name = hotel_detail["name"]
    hotel_id = hotel_detail["hotelId"]

    try:
        existing_hotel = Hotel.objects.get(hotel_id=hotel_id)
        print(existing_hotel.image.data)
        return existing_hotel.image.data
    except Hotel.DoesNotExist:
        image_data = b""
        print(1)
        try:
            params = {
                "location": coord,
                "radius": "30",
                "keyword": name,
                "key": api_key
            }
            response = requests.get(url, params=params)
            data = response.json()

            if data.get('results'):
                photos = data['results'][0].get('photos')
                photo_reference = photos[0].get('photo_reference', '') if photos else ''
            else:
                photo_reference = ''

            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={api_key}"
            response = requests.get(photo_url, stream=True)

            if response.status_code == 200:
                # Try to open the content as an image
                try:
                    Image.open(BytesIO(response.content))
                    image_data = response.content
                except UnidentifiedImageError:
                    print("The content could not be identified as an image.")
        except Exception as e:
            print(2)
            print(f"An error occurred: {e}")
            return b""

        if image_data:
            try:
                # Create new Image instance and save it
                image = Img(data=image_data)
                image.save()
                new_hotel = Hotel(
                    hotel_id=hotel_id,
                    hotel_name=name,
                    lat=lat,
                    lng=lng,
                    image=image
                )
                new_hotel.save()
            except Exception as e:
                print(f"An error occurred while saving the image and hotel data: {e}")
                return b""
        else:
            return b""
        print(image)
        return image.data


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
