from datashape import Decimal
from django.core.checks import messages
from amadeus import amadeus
from django.http import JsonResponse, HttpResponseRedirect
import json
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

from .forms import EmailUserCreationForm
from .models import Product
from .order.models import Order

api_key = 'nc3HcfEOuEoLQ8tKgGmXemwP8XkfDKbs'
api_secret = 'slE8rqApxZBdXCU5'
USERNAME = None

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from oscar.apps.catalogue.models import Product



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


class MyLoginView(LoginView):
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')

        if not remember_me:
            self.request.session.set_expiry(0)

        next_url = self.request.GET.get('next')
        if next_url:
            return redirect(next_url)

        return super().form_valid(form)


def access_token_builder(api_key, api_secret):
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
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


from oscar.apps.catalogue.models import Product
from oscar.apps.partner.models import Partner
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.apps.catalogue.models import ProductCategory
import locale
from background_task import background
from oscar.apps.catalogue.categories import create_from_breadcrumbs


class HandleHotel:
    def __init__(self):
        self.hotels_list = {}
        self.remove_hotels(offer_id=None)

    def remove_hotels(self, offer_id):
        if offer_id is None:
            Product.objects.all().delete()
        elif self.hotels_list is {}:
            pass
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


def delete_child_product(title, parent_title):
    try:
        parent_product = Product.objects.get(title=parent_title, structure=Product.PARENT)
        child_product = Product.objects.get(title=title, parent=parent_product)
        child_product.delete()
        print(f"Deleted child product with title {title} under parent product {parent_title}")
    except Product.DoesNotExist:
        print(f"Child product with title {title} under parent product {parent_title} does not exist")


def delete_parent_product(title):
    try:
        product = Product.objects.get(title=title, structure=Product.PARENT)
        product.delete()
        print(f"Deleted parent product with title {title}")
    except Product.DoesNotExist:
        print(f"Parent product with title {title} does not exist")


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


def add_parent_product(title, description, category, partner="Default Partner"):
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
    else:
        parent_product = Product.objects.get(title=title)
        print(f"Found existing product: {parent_product}")

    return parent_product


handel = HandleHotel()
handel.remove_hotels(offer_id=None)

access_token = access_token_builder(api_key=api_key, api_secret=api_secret)


class AccountRegistrationView(CoreAccountRegistrationView):
    form_class = EmailUserCreationForm


def create_new_category(category_name):
    return create_from_breadcrumbs(category_name)


@login_required(login_url='/accounts/login/')
@require_http_methods(["GET"])
def book(request, offer_id, hotel_name, price):
    # price = float(price) * float(request.session["roomQuantity"])
    request.session['offer_id'] = offer_id
    return render(request, 'checkout/payment-details/',
                  {'offer_id': offer_id, 'hotel_name': hotel_name, 'price': price})


from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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


def remove_handle_payment(request):
    keys_to_remove = ['title', 'first_name', 'last_name', 'phone', 'email', 'payment_method',
                      'card_vendor_code', 'card_number', 'card_expiry_date']

    for key in keys_to_remove:
        if key in request.session:
            del request.session[key]


def home(request):
    return render(request, 'index.html')


from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView


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
from django.urls import reverse
from oscar.apps.checkout.mixins import OrderPlacementMixin
from oscar.apps.partner.strategy import Selector
from oscar.apps.basket.models import Basket
from oscar.apps.order.utils import OrderCreator
from oscar.core.loading import get_class

OrderTotalCalculator = get_class('checkout.calculators', 'OrderTotalCalculator')

from oscar.core.prices import Price

from oscar.core.loading import get_model, get_class


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
                                    phone=phone, email=email, method=payment_method, vendor_code=card_vendor_code,
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


class AddElementsToOrderView(View):
    def post(self, request):
        order_number = request.POST.get('order_number')
        add_new_elements_to_order(request, order_number)
        return JsonResponse({'status': 'ok'})


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


def get_username(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.email
    return username


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
    handel.remove_hotels(offer_id=None)
    hotel_offers = get_hotel_offer_list(lat=lat, lng=lng, checkInDate=checkInDate, category=category,
                                        checkOutDate=checkOutDate, adults=adults, roomQuantity=roomQuantity)
    user, domain = username.split('@')
    dom, dotdomain = domain.split('.')
    user = user + dom + dotdomain
    # products_less_than_5_stars = Product.objects.annotate(avg_rating=Avg('ratingproduct__rating')).filter(avg_rating__lt=5)

    return redirect(f'/catalogue/category/{user}_{category.id}/', hotel_offers)


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
    handel.remove_hotels(offer_id=None)
    hotel_offers = get_hotel_offer_list(lat=lat, lng=lng, checkInDate=checkInDate, category=category,
                                        checkOutDate=checkOutDate, adults=adults, roomQuantity=roomQuantity,
                                        hotel_id=hotel_id)
    user, domain = username.split('@')
    dom, dotdomain = domain.split('.')
    user = user + dom + dotdomain
    return redirect(f'/catalogue/category/{user}_{category.id}/', hotel_offers)


from oscar.apps.catalogue.views import ProductCategoryView


class CustomProductCategoryView(ProductCategoryView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(avg_rating=Avg('reviews__rating')).exclude(avg_rating=5)


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


@require_http_methods(["GET"])
def hotels(request):
    username = get_username(request=request)
    user, domain = username.split('@')
    dom, dotdomain = domain.split('.')
    user = user + dom + dotdomain
    category = create_new_category(category_name=user)

    return render(request, f'/catalogue/category/{user}_{category.id}/')


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


def get_hotel_geo_list(latitude, longitude):
    url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-geocode"

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
from oscar.apps.catalogue.models import Product


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


def get_hotel_offer_list(lat, lng, category, checkInDate, checkOutDate, adults, roomQuantity, paymentPolicy="NONE",
                         bestRateOnly="false", hotel_id=None):
    url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
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
        hotel_id = [d["hotelId"] for d in hotel_ids_data["data"]]
        print(hotel_id)
        for hotel in hotel_ids_data["data"]:
            if hotel["hotelId"] == 'MCLONGHM' or hotel["hotelId"] == 'PILONBAK':
                hotel_ids_d.append(hotel)
        # id=get_hotel_geo_list(latitude=lat, longitude=lng)
        # print(id)
        hotel_ids.append("MCLONGHM")
        hotel_ids.append("PILONBAK")
        # hotel_ids.append("BGLONBGB")

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
        data = response.json()
        for item in data['data']:
            hotel_id = item['hotel']['name']
            hotel_stars = hotel_ids_d[0]['rating'] if hotel_ids_d != [] else 5
            handel.hotels_list[hotel_id] = []
            hotel_details = {
                'name': item['hotel']['name'],
                'hotelId': item['hotel']['hotelId'],
                'cityCode': item['hotel']['cityCode'],
                'chainCode': hotel_ids_d[0]['chainCode'] if hotel_ids_d != [] else "None",
                'iataCode': hotel_ids_d[0]['iataCode'] if hotel_ids_d != [] else "None",
                'dupeId': hotel_ids_d[0]['dupeId'] if hotel_ids_d != [] else "None",
                'geoCode': "latitude: " + str(hotel_ids_d[0]['geoCode']['latitude']) + " longitude: " + str(
                    hotel_ids_d[0]['geoCode']['longitude']) if hotel_ids_d != [] else "None",
                'address': hotel_ids_d[0]['address']['countryCode'] if hotel_ids_d != [] else "None",
                'distance': str(hotel_ids_d[0]['distance']['value']) + str(hotel_ids_d[0]['distance'][
                                                                               'unit']) + " from location" if hotel_ids_d != [] else "None",
                'amenities': ' , '.join(hotel_ids_d[0]['amenities']) if hotel_ids_d != [] else "None",
                'rating': hotel_ids_d[0]['rating'] if hotel_ids_d != [] else "None",
                'giataId': hotel_ids_d[0]['giataId'] if hotel_ids_d != [] else "None",
                'lastUpdate': hotel_ids_d[0]['lastUpdate'] if hotel_ids_d != [] else "None",

            }
            parent_description = json.dumps(hotel_details, indent=4)
            print(parent_description)
            parent_product = add_parent_product(title=hotel_id, description=parent_description, category=category)
            update_product_review_score(parent_product, hotel_stars)
            childs_list = []
            for offer in item['offers']:
                offer_id = offer['id']
                offer_name = offer_id + "," + offer['room']['typeEstimated']['category']
                handel.hotels_list[hotel_id].append(offer_id)
                hotel_data = {
                    'checkInDate': offer.get('checkInDate', None),
                    'checkOutDate': offer.get('checkOutDate', None),
                    'rateCode': offer.get('rateCode', None),
                    'room type': offer['room']['type'] if offer else None,
                    'room type category': offer['room']['typeEstimated']['category'] if offer else None,
                    'room type beds': offer['room']['typeEstimated']['beds'] if offer else None,
                    'room type bedType': offer['room']['typeEstimated']['bedType'] if offer else None,
                    'room lang': offer['room']['description']['lang'] if offer else None,
                    'room description': offer['room']['description']['text'] if offer else None,
                    'adults': offer['guests']['adults'] if offer else None,
                    'price currency': offer['price']['currency'] if offer else None,
                    'price total': offer['price']['total'] if offer else None,
                    # 'price taxes': offer['price']['taxes'],
                    'cancellations': offer['policies']['cancellations'] if offer else None,
                    # 'price changes startDate': offer['price']['changes']['startDate'],
                    # 'price changes endDate': offer['price']['changes']['endDate'],
                    # 'price changes total': offer['price']['changes']['total'],
                    'changes': offer.get('changes', None),
                    'price': offer.get('price', None),
                    # 'guarantee': ' '.join(offer['policies']['guarantee']['acceptedPayments']['creditCards']),
                    # 'paymentType': ' '.join(offer['paymentType']),
                    ##'price taxes code': offer['price']['taxes']['code'],
                    ##'price taxes pricingFrequency': offer['price']['taxes']['pricingFrequency'],
                    ##'price taxes pricingMode': offer['price']['taxes']['pricingMode'],
                    ##'price taxes amount': offer['price']['taxes']['amount'],
                    ##'price taxes currency': offer['price']['taxes']['currency'],
                    ##'price taxes included': offer['price']['taxes']['included'],
                }
                hotel_description = json.dumps(hotel_data, indent=4)  # Convert the hotel data to a JSON string
                currency = hotel_data['price']['currency'] if hotel_data.get('price') else None
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


def post_booking(offer_id, title, first_name, last_name, phone, email, method, vendor_code, card_number, expiry_date):
    url = "https://test.api.amadeus.com/v1/booking/hotel-bookings"

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


def hotel_auto_complete(name):
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    url = 'https://test.api.amadeus.com/v1/reference-data/locations/hotel'
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


def update_product_review_score(product, new_score):
    # Get the reviews of the product
    reviews = ProductReview.objects.filter(product=product)
    product.rating = new_score
    product.save()


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


@login_required(login_url='/accounts/login/')
@require_http_methods(["GET", "POST"])
def alerts_list(request):
    alerts = PriceAlert.objects.filter(user=request.user)
    return render(request, 'oscar/customer/alerts/alert_list.html', {'alerts': alerts})


def delete_alert(request, alert_id):
    alert = PriceAlert.objects.get(pk=alert_id)
    alert.delete()
    return redirect('price_alerts')


def price_alerts(request):
    alerts = PriceAlert.objects.all()
    return render(request, 'price_alerts.html', {'alerts': alerts})


from oscar.apps.catalogue.models import Product


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
