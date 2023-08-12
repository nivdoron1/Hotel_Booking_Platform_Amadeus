import json
import locale

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
from .product import images_of_hotel, add_parent_product, update_product_review_score, add_child_product, HandleHotel

"""
Builds an access token for the API.
@param api_key: The API key.
@param api_secret: The API secret.
@return: The access token.
"""
load_dotenv()

GEO_API_KEY = os.getenv('GEO_API_KEY')

handel = HandleHotel()


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


def get_hotel_offer_list(access_token, username, lat, lng, category, checkInDate, checkOutDate, adults, roomQuantity,
                         paymentPolicy="NONE",
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
        hotel_ids_data = get_hotel_geo_list(access_token=access_token, latitude=lat, longitude=lng)
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

            parent_product = add_parent_product(title=username + "," + hotel_id, description=parent_description,
                                                image_data=image,
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


def post_booking(access_token, offer_id, title, first_name, last_name, phone, email, method, vendor_code, card_number,
                 expiry_date):
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


def hotel_auto_complete(access_token, name):
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


"""
This function fetches a list of hotels in a specific city. It calls the Amadeus API and returns a list of hotels
based on the provided city code.

:param cityCode: str, The code of the city to fetch hotels.
:return: json response containing hotels data.
"""


def get_hotel_city_list(access_token, cityCode):
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

    # Parameters for the API request
    params = {
        'key': GEO_API_KEY,
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


def get_hotel_geo_list(access_token, latitude, longitude):
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
