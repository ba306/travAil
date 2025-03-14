from django import forms
from django.core.validators import EmailValidator

class SearchForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    num_adults = forms.IntegerField(min_value=1, max_value=10)
    max_price = forms.IntegerField(min_value=0)
    email = forms.CharField(validators=[EmailValidator()], widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    ne_lat = forms.FloatField(widget=forms.HiddenInput())  # Hidden field
    ne_lng = forms.FloatField(widget=forms.HiddenInput())  # Hidden field
    sw_lat = forms.FloatField(widget=forms.HiddenInput())  # Hidden field
    sw_lng = forms.FloatField(widget=forms.HiddenInput())  # Hidden field