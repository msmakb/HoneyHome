from django import forms
from django.forms import ModelForm
from main.models import Person
from .models import Customer, Questionnaire


class DateInput(forms.DateInput):
    input_type = 'date'

class AddPersonForm(ModelForm):
    class Meta:
        model = Person
        fields = [
            'name',
            'gender',
            'nationality',
            'date_of_birth',
            'address',
            'contacting_email',
            'phone_number',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Full Name'}),
            'gender': forms.Select(attrs={'required': False, 'class': 'form-control'}),
            'nationality': forms.Select(attrs={'required': False, 'class': 'form-control'}),
            'date_of_birth': DateInput(attrs={'required': False, 'class': 'form-control', 'data-provide':'datepicker'}),
            'address': forms.TextInput(attrs={'required': False, 'class': 'form-control','placeholder': 'Address'}),
            'contacting_email': forms.EmailInput(attrs={'required': False, 'class': 'form-control', 'placeholder': 'Contacting Email'}),
            'phone_number': forms.TextInput(attrs={'required': False, 'class': 'form-control', 'placeholder': 'Phone number'}),
        }

class AddCustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = [
            'instagram',
            'facebook',
            'shopee',
        ]
        widgets = {
            'instagram': forms.TextInput(attrs={'required': False, 'class': 'form-control', 'placeholder': 'Customer Instagram Account'}),
            'facebook': forms.TextInput(attrs={'required': False, 'class': 'form-control', 'placeholder': 'Customer Facebook Account'}),
            'shopee': forms.TextInput(attrs={'required': False, 'class': 'form-control', 'placeholder': 'Customer Shopee Account'}),
        }

class CreateQuestionnaireForm(ModelForm):
    class Meta:
        model = Questionnaire
        fields = [
            'title',
            'description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Questionnaire Title'}),
            'description': forms.Textarea(attrs={'required': False, 'class': 'form-control', 'placeholder': 'Questionnaire Description'}),
        }

class PublishQuestionnaireForm(forms.Form):
        widgets = forms.NumberInput(attrs={'required': False, 'class': 'form-control', 'placeholder': 'Questionnaire Period (NOT REQUIRED)'})
        period = forms.IntegerField(widget=widgets)
