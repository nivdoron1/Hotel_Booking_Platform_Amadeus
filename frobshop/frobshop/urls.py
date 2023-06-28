"""frobshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.views.generic import RedirectView

from . import views
# from frobshop.checkout import ShippingAddressView, ShippingMethodView, PaymentDetailsView
from .views import *
from .views import MyLoginView
from .views import add_to_basket_and_checkout
from .views import alerts_list

urlpatterns = [
                  # path('', views.index, name='home'),  # Move this to the top
                  path('i18n/', include('django.conf.urls.i18n')),
                  path('admin/', admin.site.urls),
                  path('', index, name='index'),
                  path('complete_purchase/', views.complete_purchase, name='complete_purchase'),

                  path('catalogue/', RedirectView.as_view(url='/'), name='home'),
                  # path('catalogue/', RedirectView.as_view(url='/accounts'), name='home'),
                  path('', include(apps.get_app_config('oscar').urls[0])),
                  path('dashboard/accounts/', apps.get_app_config('accounts_dashboard').urls),
                  path('book', views.book, name='book'),
                  path('confirm', views.confirm, name='confirm'),
                  path('search', views.search, name='search'),
                  path('hotel_view', views.hotel_view, name='hotel_view'),
                  path('handle-payment/', handle_payment, name='handle_payment'),
                  path('hotel_search_auto_complete', views.hotel_search_auto_complete,
                       name='hotel_search_auto_complete'),
                  path('hotels', views.hotels, name='hotels'),
                  path('catalogue/category/<str:username>_<int:category_id>/', views.CustomProductCategoryView.as_view(),
                       name='category'),
                  path('filter_products/', views.ProductFilterView.as_view(), name='filter_products'),
                  path('price_alerts/get_hotel_offer/<int:alert_id>/', views.get_hotel_offer, name='get_hotel_offer'),
                  path('get_hotel_offers', views.get_hotel_offers, name='get_hotel_offers'),
                  path('catalogue/category/<str:username>_<int:category_id>/', views.get_hotel_offers,
                       name='get_hotel_offers'),
                  path('book/<str:offer_id>/<str:hotel_name>/<str:price>/', views.book, name='book'),
                  path('', home, name='home'),
                  path('accounts/login/', MyLoginView.as_view(), name='login'),
                  path('add_to_basket_and_checkout/<int:product_id>/', add_to_basket_and_checkout,
                       name='add_to_basket_and_checkout'),
                  path('product_management/', include('product_management.urls')),
                  path('customer/alerts/alert_list', views.hotel_view, name='hotel_view'),
                  path('customer/alerts/', price_alerts, name='price_alerts'),
                  path('price_alerts/', views.price_alerts, name='price_alerts'),
                  path('price_alerts/delete/<int:alert_id>/', views.delete_alert, name='delete_alert'),
                  path('payment-details/', views.PaymentDetailsView.as_view(), name='payment-details'),
                  path('api/add-elements-to-order/', views.AddElementsToOrderView.as_view(),
                       name='add_elements_to_order'),

              ] + static(settings.MEDIA_URL,
                         document_root=settings.MEDIA_ROOT)
