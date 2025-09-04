from django import forms

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120, label="Full name")
    phone = forms.CharField(max_length=30, label="Phone number")
    address_line1 = forms.CharField(max_length=255, label="Address line 1")
    address_line2 = forms.CharField(max_length=255, label="Address line 2", required=False)
    city = forms.CharField(max_length=120)
    country = forms.CharField(max_length=120, initial="Kenya")
