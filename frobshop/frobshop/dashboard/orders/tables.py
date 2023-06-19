import django_tables2 as tables
from oscar.apps.order.models import Order


class CustomOrderTable(tables.Table):
    confirmation_hotel_number = tables.Column(verbose_name='Confirmation Hotel Number', orderable=True,
                                              accessor='confirmation_hotel_number')

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap.html'
        fields = ('number', 'total_excl_tax', 'date_placed', 'status',
                  'confirmation_hotel_number')  # add other fields if necessary


# Fetch all Orders
orders = Order.objects.all()

# Print them out
for order in orders:
    print(f"Order number: {order.number}, Total price: {order.total_incl_tax}")
