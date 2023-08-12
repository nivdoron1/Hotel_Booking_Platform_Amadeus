from io import BytesIO
import requests
from PIL import Image
from PIL import UnidentifiedImageError
from dotenv import load_dotenv
import os
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Avg
from hotels.models import Hotel
from hotels.models import Image as Img
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.apps.catalogue.models import ProductCategory
from oscar.apps.catalogue.models import ProductImage
from oscar.apps.catalogue.reviews.models import ProductReview
from oscar.apps.catalogue.views import ProductCategoryView
from oscar.apps.partner.models import Partner, StockRecord
from oscar.apps.partner.strategy import Selector
from oscar.core.loading import get_model

from .models import Product

Product = get_model('catalogue', 'product')
ProductImage = get_model('catalogue', 'ProductImage')

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

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


"""
Adds a parent product to the database.
@param title: The title of the parent product.
@param description: The description of the parent product.
@param category: The category of the parent product.
@param partner: The partner of the parent product (default is "Default Partner").
@return: The added parent product.
"""


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


"""
Creates a new category.
@param category_name: The name of the category.
@return: The created category.
"""


def create_new_category(category_name):
    return create_from_breadcrumbs(category_name)


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


class HandleHotel:
    """
    Constructor for the HandleHotel class.
    """

    def __init__(self):
        self.hotels_list = {}
        # self.remove_hotels(offer_id=None)

    """
    Removes hotels from the database.

    @param offer_id: The ID of the offer to remove. If None, removes all hotels.
    """

    def remove_hotels(self, offer_id, category):
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
* A custom class-based view to display a list of products in a category, excluding 5-star products.
*
* @returns A queryset of products that is displayed in the view.
"""


class CustomProductCategoryView(ProductCategoryView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(avg_rating=Avg('reviews__rating')).exclude(avg_rating=5)


def update_product_review_score(product, new_score):
    # Get the reviews of the product
    reviews = ProductReview.objects.filter(product=product)
    product.rating = new_score
    product.save()



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


def images_of_hotel(hotel_detail):
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
                "key": GOOGLE_API_KEY
            }
            response = requests.get(url, params=params)
            data = response.json()

            if data.get('results'):
                photos = data['results'][0].get('photos')
                photo_reference = photos[0].get('photo_reference', '') if photos else ''
            else:
                photo_reference = ''

            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_API_KEY}"
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
