from django import forms

class SearchForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    num_adults = forms.IntegerField(min_value=1, max_value=10)
    max_price = forms.IntegerField(min_value=0)
    ne_lat = forms.FloatField()
    ne_lng = forms.FloatField()
    sw_lat = forms.FloatField()
    sw_lng = forms.FloatField()
