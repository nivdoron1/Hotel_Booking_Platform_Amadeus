from django import forms
from django.utils.translation import gettext_lazy as _

from oscar.apps.customer.forms import EmailUserCreationForm as CoreEmailUserCreationForm
from oscar.core.compat import (existing_user_fields, get_user_model)
from oscar.apps.customer.forms import EmailUserCreationForm

User = get_user_model()


class CustomEmailUserCreationForm(EmailUserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta(EmailUserCreationForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


class PaymentForm(forms.Form):
    title = forms.CharField(max_length=200)
    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    phone = forms.CharField(max_length=200)
    email = forms.EmailField()
    method = forms.CharField(max_length=200)
    vendor_code = forms.CharField(max_length=200)
    card_number = forms.CharField(max_length=200)
    expiry_date = forms.DateField()
