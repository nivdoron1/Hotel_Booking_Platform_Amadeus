from django_tables2 import SingleTableView
from oscar.apps.dashboard.orders.views import OrderListView as CoreOrderListView
from .tables import CustomOrderTable
from oscar.apps.order.models import Order


class OrderListView(CoreOrderListView, SingleTableView):
    table_class = CustomOrderTable
    context_table_name = 'orders'
    template_name = 'dashboard/orders/'  # path to your template

    def get_table(self, **kwargs):
        table_pagination = {"per_page": self.descendants}
        return CustomOrderTable(self.get_table_data(), order_by=self.get_default_order_by(), **kwargs)

    def get_table_data(self):
        return Order.objects.all()  # Customize this to change the data that populates the table

    def get_default_order_by(self):
        return "-date_placed"

# Add other views if necessary...
