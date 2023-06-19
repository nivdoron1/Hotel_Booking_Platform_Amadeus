from django.http import HttpResponse
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.apps.catalogue.models import Product, ProductClass, ProductAttribute, ProductAttributeValue
from oscar.apps.partner.models import Partner, StockRecord


def add_product_view(request):
    # Create or get the product class
    product_class, created = ProductClass.objects.get_or_create(name='Books')

    # Create or get a category
    category = create_from_breadcrumbs('Books>Fiction>Fantasy')

    # Create the product
    product = Product.objects.create(
        title='Harry Potter',
        product_class=product_class,
    )
    product.categories.add('BOOK')
    product.categories.add(category)

    # Add product attributes
    attribute = ProductAttribute.objects.create(
        product_class=product_class,
        name='Author',
    )
    ProductAttributeValue.objects.create(
        product=product,
        attribute=attribute,
        value='J. K. Rowling',
    )

    # Create or get a partner
    partner, created = Partner.objects.get_or_create(name='Warehouse')

    # Create a stock record
    stock_record = StockRecord.objects.create(
        product=product,
        partner=partner,
        price_excl_tax=9.99,
        price_retail=9.99,
        cost_price=5,
        num_in_stock=10,
    )

    # Save the product
    product.save()

    return HttpResponse('Product added successfully')
