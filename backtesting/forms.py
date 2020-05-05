from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class sma_search(forms.Form):
    ticker = forms.CharField(label='Stock ticker')
    #start_date = forms.DateField(label='Start date')
    start_date = forms.DateField(label='Start date, Format YYYY-MM-DD', input_formats=['%Y-%m-%d'])
    end_date = forms.DateField(label='End date, Format YYYY-MM-DD', input_formats=['%Y-%m-%d'])
    sma_fast = forms.IntegerField(label='SMA, fast')
    sma_slow = forms.IntegerField(label='SMA, slow')
