from django import forms

class CitySelectionForm(forms.Form):
    start_city = forms.ChoiceField(label="Start City")
    end_city = forms.ChoiceField(label="End City")
