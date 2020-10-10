from django import forms
from .db_scripts import CarMakeDB, CarModelDB


cm = CarMakeDB()
MAKES_CHOICES = [(x[0].lower().capitalize(), x[0].lower().capitalize()) for x in cm.GetAllMakes()]
MAKES_CHOICES.insert(0, ('', '-------'))
cm._dconnect()

STARS_CHOICES = [(i,i) for i in range(6)]
STARS_CHOICES.insert(0, ('', '-------'))

pc = ['Full', 'MSRP']
PRICES_CHOICES = [(i, i) for i in pc]
PRICES_CHOICES.insert(0, ('', '-------'))


class InputForm(forms.Form):
    email = forms.EmailField(required=True)
    zip_code = forms.IntegerField(required=True)
    dist = forms.IntegerField(required=True)
    minimum_stars = forms.ChoiceField(initial='-------',
                                      label='Enter the minimum star rating for dealerships you want to search',
                                      choices=STARS_CHOICES, required=True)
    car_make = forms.ChoiceField(initial='-------',
                                 label='Choose a car make from the dropdown below',
                                 choices=MAKES_CHOICES, required=True)
    car_model = forms.CharField(max_length=40, required=True)
    prices = forms.ChoiceField(initial='-------',
                             label='Enter whether or not you would like to see prices with discounts or just the MSRP',
                             choices=PRICES_CHOICES, required=False)