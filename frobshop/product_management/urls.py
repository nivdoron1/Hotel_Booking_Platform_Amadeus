from django.urls import path
from .views import add_product_view

urlpatterns = [
    path('add_product/', add_product_view),
    path('add_hotel/', add_product_view),

]
