from datashape import Decimal
from django.http import JsonResponse
import json
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import path
from django.views.decorators.http import require_http_methods
from oscar.apps.catalogue.models import Category, ProductCategory, Product
from oscar.apps.customer.views import AccountRegistrationView as CoreAccountRegistrationView
from oscar.apps.partner.models import Partner, StockRecord
from oscar.apps.partner.strategy import Selector
from requests.auth import HTTPBasicAuth

from .forms import EmailUserCreationForm
from .models import Product

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
        print(f"Creating product with category ID: {category.id}")
        parent_product = Product.objects.create(title=title,
                                                description=description,
                                                product_class_id=3,
                                                structure=Product.PARENT)  # Use appropriate product class id

        print(f"Product created: {parent_product}")
        product_category = ProductCategory.objects.create(product=parent_product, category=category)
        print(f"ProductCategory created: {product_category}")
    else:
        parent_product = Product.objects.get(title=title)
        print(f"Found existing product: {parent_product}")

    return parent_product


handel = HandleHotel()
handel.remove_hotels(offer_id=None)


@background(schedule=600)  # Schedule task to run after 600 seconds i.e. 10 minutes
def check_out(request):
    # Code to add products...

    # Schedule the task
    handel.remove_hotels(offer_id=None)

    # Redirect to index
    return redirect('index')  # Assuming 'index' is the name of your homepage view


@background(schedule=5)  # Schedule task to run after 600 seconds i.e. 10 minutes
def hotels_pick(request):
    # Code to add products...

    # Schedule the task
    handel.remove_hotels(offer_id=None)

    # Redirect to index
    return redirect('index')  # Assuming 'index' is the name of your homepage view


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
    return render(request, 'book.html', {'offer_id': offer_id, 'hotel_name': hotel_name, 'price': price})


def home(request):
    return render(request, 'index.html')


@require_http_methods(["POST"])
def confirm(request):
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

    return render(request, 'confirmation.html', {'booking_data': booking_response})


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

    handel.remove_hotels(offer_id=None)
    hotel_offers = get_hotel_offer_list(lat=lat, lng=lng, checkInDate=checkInDate, category=category,
                                        checkOutDate=checkOutDate, adults=adults, roomQuantity=roomQuantity)
    user, domain = username.split('@')
    dom, dotdomain = domain.split('.')
    user = user + dom + dotdomain
    return redirect(f'/catalogue/category/{user}_{category.id}/', hotel_offers)


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
        "radiusUnit": "KM",
        "hotelSource": "ALL",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
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
        "hotelSource": "ALL",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to get data:", response.status_code)


def get_hotel_offer_list(lat, lng, category, checkInDate, checkOutDate, adults, roomQuantity, paymentPolicy="NONE",
                         bestRateOnly="false"):
    url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    hotel_ids = []
    # hotel_ids=get_hotel_geo_list(latitude=lat,longitude=lng,access_token=access_token)
    ##hotel_ids = [d["hotelId"] for d in data["data"]]
    hotel_ids.append("PILONBBY")
    hotel_ids.append("PILONBAK")
    hotel_ids.append("BGLONBGB")
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
            handel.hotels_list[hotel_id] = []
            hotel_details = {
                'name': item['hotel']['name'],
                'hotelId': item['hotel']['hotelId'],
                'cityCode': item['hotel']['cityCode'],
            }
            parent_description = json.dumps(hotel_details, indent=4)
            parent_product = add_parent_product(title=hotel_id, description=parent_description, category=category)
            for offer in item['offers']:
                offer_id = offer['id']
                handel.hotels_list[hotel_id].append(offer_id)
                hotel_data = {
                    'checkInDate': offer.get('checkInDate', None),
                    'checkOutDate': offer.get('checkOutDate', None),
                    'rateCode': offer.get('rateCode', None),
                    'rateFamilyEstimated': offer.get('rateFamilyEstimated', None),
                    'room': offer.get('room', None),
                    'guests': offer.get('guests', None),
                    'price': offer.get('price', None),
                    'policies': offer.get('policies', None),
                    'self': offer.get('self', None)
                }
                hotel_description = json.dumps(hotel_data, indent=4)  # Convert the hotel data to a JSON string
                currency = hotel_data['price']['currency'] if hotel_data.get('price') else None
                total_price = locale.atof(hotel_data['price']['total']) * float(roomQuantity) if hotel_data.get(
                    'price') else 0
                add_child_product(parent_product=parent_product, description=hotel_description,
                                  price=total_price, currency=currency, title=offer_id)
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
        handel.remove_hotels(offer_id=offer_id)
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


@require_http_methods(["GET"])
def hotel_search_auto_complete(request):
    search_query = request.GET.get('query', '')
    print("this is the search query:")
    print(search_query)
    data_list = []
    if len(search_query) >= 3:
        data = hotel_auto_complete(search_query)
        for dat in data["data"]:
            data_list.append(dat["name"])
            print(dat["name"])
    return JsonResponse({'features': data_list})


"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import HotelBooking

@login_required
@require_http_methods(["POST"])
def create_booking(request):
    # Extract data from form submission
    hotel_name = request.POST.get('location')
    check_in_date = request.POST.get('checkInDate')
    check_out_date = request.POST.get('checkOutDate')
    number_of_adults = request.POST.get('adults')
    number_of_rooms = request.POST.get('roomQuantity')
    price = request.POST.get('price')

    # Create new HotelBooking
    booking = HotelBooking(
        user=request.user,
        hotel_name=hotel_name,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        number_of_adults=number_of_adults,
        number_of_rooms=number_of_rooms,
        price=price
    )
    try:
        booking.save()
        return JsonResponse({
            'email': request.user.email,
            'hotel_name': booking.hotel_name,
            'check_in_date': booking.check_in_date,
            'check_out_date': booking.check_out_date,
            'number_of_adults': booking.number_of_adults,
            'number_of_rooms': booking.number_of_rooms,
            'price': booking.price,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
"""

# URLs mapping

urlpatterns = [
    path('', index, name='index'),
    path('search', search, name='search'),
    path('hotel_search_auto_complete', hotel_search_auto_complete, name='hotel_search_auto_complete'),
    path('hotels', hotels, name='hotels'),
    path('get_hotel_offers', get_hotel_offers, name='get_hotel_offers'),
    path('book', book, name='book'),
    path('confirm', confirm, name='confirm'),
]
