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


access_token = access_token_builder(api_key=api_key, api_secret=api_secret)


class AccountRegistrationView(CoreAccountRegistrationView):
    form_class = EmailUserCreationForm


@login_required(login_url='/accounts/login/')
@require_http_methods(["GET"])
def book(request, offer_id, hotel_name, price):
    price = float(price) * float(request.session["roomQuantity"])
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
    hotel_offers = get_hotel_offer_list(lat=lat, lng=lng, checkInDate=checkInDate,
                                        checkOutDate=checkOutDate, adults=adults, roomQuantity=roomQuantity)
    return render(request, 'hotels.html', {'hotel_offers': hotel_offers, 'lat': lat, 'lng': lng, 'location': location,
                                           'roomQuantity': roomQuantity})


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
    return render(request, 'hotels.html')


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


def get_hotel_offer_list(lat, lng, checkInDate, checkOutDate, adults, roomQuantity, paymentPolicy="NONE",
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
    print(response.url)
    if response.status_code == 200:
        data = response.json()
        for dat in data['data']:
            add_parent_product(dat['hotel']['hotelId'], description="!")
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
        return response.json()
    else:
        print("Failed to post booking:", response.status_code, response.text)
        return None


def add_parent_product(title, description, partner="Default Partner"):
    partner, created = Partner.objects.get_or_create(name=partner)
    parent_product = None
    # Check if the parent product already exists
    if not Product.objects.filter(title=title).exists():
        # Create the parent product
        parent_product = Product.objects.create(title=title,
                                                description=description,
                                                product_class_id=3,
                                                structure=Product.PARENT)  # Use appropriate product class id

        # Get the category to which you want to add the products
        category = Category.objects.get(name='HOTELS')  # Get category with name 'HOTELS'
        product_category = ProductCategory.objects.create(product=parent_product, category=category)
    else:
        parent_product = Product.objects.get(title=title)

    return parent_product


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


# Define parent product details
"""
parent_product_title = "w"
parent_product_description = "This is a new product"

# Get or create a partner
partner, created = Partner.objects.get_or_create(name="Default Partner")
parent_product = None
# Check if the parent product already exists
if not Product.objects.filter(title=parent_product_title).exists():
    # Create the parent product
    parent_product = Product.objects.create(title=parent_product_title,
                                            description=parent_product_description,
                                            product_class_id=3,
                                            structure=Product.PARENT)  # Use appropriate product class id

    # Get the category to which you want to add the products
    category = Category.objects.get(name='HOTELS')  # Get category with name 'HOTELS'
    product_category = ProductCategory.objects.create(product=parent_product, category=category)
    # Create child products
    """
# parent_product = add_parent_product(title="kdlkdldklkl", description="flf", partner=partner)
# print(parent_product)
# add_child_product(title="child", description="fklf", parent_product=parent_product, currency='GBP', price=10)


"""for i in range(3):
    child_product_title = f"Child Product {i+2}"
    child_product_description = f"This is child product {i+1}"
    # child_product = None
    add_child_product(title=child_product_title, description=child_product_description, parent_product=parent_product,
                      currency='GBP', price=10, partner=partner)"""
"""if not Product.objects.filter(title=child_product_title,parent=parent_product).exists():
    child_product = Product.objects.create(
        title=child_product_title,
        description=child_product_description,
        parent=parent_product,
        structure=Product.CHILD
    )

    # Generate SKU from the product title
    sku = child_product_title.replace(" ", "_").upper()

    # Create a stock record for the child product
    stock_record = StockRecord.objects.create(
        product=child_product,
        partner=partner,
        partner_sku=sku,  # Replace with your unique SKU
        price_currency='GBP',  # Replace with your preferred currency
        price=100,  # Replace with your price
        num_in_stock=50,  # Replace with your stock quantity
        num_allocated=0,  # Replace with your allocated stock quantity
        low_stock_threshold=2,  # Replace with your low stock threshold
    )
    stock_record.save()
    # Fetch the price and availability using the strategy framework
    strategy = Selector().strategy(request=None, user=None)
    info = strategy.fetch_for_product(child_product)
    child_product.save()"""
# URLs mapping

urlpatterns = [
    path('', index, name='index'),
    path('search', search, name='search'),
    path('hotels', hotels, name='hotels'),
    path('get_hotel_offers', get_hotel_offers, name='get_hotel_offers'),
    path('book', book, name='book'),
    path('confirm', confirm, name='confirm'),
]
