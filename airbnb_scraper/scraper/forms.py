from django import forms
from django.core.validators import EmailValidator

class SearchForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    num_adults = forms.IntegerField(min_value=1, max_value=10)
    max_price = forms.IntegerField(min_value=0)
    email = forms.CharField(validators=[EmailValidator()], widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    ne_lat = forms.FloatField(widget=forms.HiddenInput())
    ne_lng = forms.FloatField(widget=forms.HiddenInput())
    sw_lat = forms.FloatField(widget=forms.HiddenInput())
    sw_lng = forms.FloatField(widget=forms.HiddenInput())
    map_center_lat = forms.FloatField(widget=forms.HiddenInput())
    map_center_lng = forms.FloatField(widget=forms.HiddenInput())
    map_zoom = forms.FloatField(widget=forms.HiddenInput())
    frequency_interval = forms.IntegerField(min_value=1, label="Frequency Interval")
    frequency_unit = forms.ChoiceField(choices=[
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
    ], label="Frequency Unit")
    min_rating = forms.FloatField(
        required=False,
        min_value=0,
        max_value=5,
        label="Minimum Rating",
        widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    min_reviews = forms.IntegerField(
        required=False,
        min_value=0,
        label="Minimum Reviews",
        widget=forms.NumberInput(attrs={'step': '1'})
    )