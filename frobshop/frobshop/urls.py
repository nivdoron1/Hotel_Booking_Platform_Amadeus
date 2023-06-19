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
from django.conf.urls import url
from django.contrib import admin
from django.urls import include
from django.views.generic import RedirectView
from . import views
# from frobshop.checkout import ShippingAddressView, ShippingMethodView, PaymentDetailsView
from .views import *
from .views import MyLoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  #path('', views.index, name='home'),  # Move this to the top
                  path('i18n/', include('django.conf.urls.i18n')),
                  path('admin/', admin.site.urls),
                  path('', index, name='index'),
                  path('catalogue/', RedirectView.as_view(url='/'), name='home'),
                  #path('catalogue/', RedirectView.as_view(url='/accounts'), name='home'),
                  path('', include(apps.get_app_config('oscar').urls[0])),
                  path('dashboard/accounts/', apps.get_app_config('accounts_dashboard').urls),
                  path('book', views.book, name='book'),
                  path('confirm', views.confirm, name='confirm'),
                  path('search', views.search, name='search'),
                  path('hotels', views.hotels, name='hotels'),
                  path('get_hotel_offers', views.get_hotel_offers, name='get_hotel_offers'),
                  path('book/<str:offer_id>/<str:hotel_name>/<str:price>/', views.book, name='book'),
                  path('', home, name='home'),
                  path('accounts/login/', MyLoginView.as_view(), name='login'),
                  # path('shipping-address/', ShippingAddressView.as_view(), name='shipping-address'),
                  # path('shipping-method/', ShippingMethodView.as_view(), name='shipping-method'),
                  # path('payment-details/', PaymentDetailsView.as_view(), name='payment-details'),
                  # path('add_product/', views.add_product, name='add_product'),
                  path('product_management/', include('product_management.urls')),
              ] + static(settings.MEDIA_URL,
                         document_root=settings.MEDIA_ROOT)
