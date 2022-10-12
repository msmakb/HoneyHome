from django import forms
from django.forms import ModelForm
from .models import Expenses, Sales

class DateInput(forms.DateInput):
    input_type = 'date'

class AddExpensesForm(ModelForm):
    class Meta:
        model = Expenses
        fields = [
            'item',
            'quantity',
            'price',
            'date',
            'note'
        ]
        widgets = {
            'item': forms.TextInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Item'}),
            'quantity': forms.NumberInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Quantity'}), 
            'price': forms.NumberInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Price'}), 
            'date': DateInput(attrs={'required': False, 'class': 'form-control', 'data-provide':'datepicker'}),
            'note': forms.Textarea(attrs={'required': False, 'class': 'form-control', 'placeholder': 'Description'}),
        }

class AddSalesForm(ModelForm):
    class Meta:
        model = Sales
        fields = [
            'type',
            'batch',
            'quantity',
            'price',
            'date',
        ]
        widgets = {
            'type': forms.Select(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Type'}),
            'batch': forms.Select(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Batch'}),
            'quantity': forms.NumberInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Quantity'}),
            'price': forms.NumberInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Price'}),
            'date': DateInput(attrs={'required': False, 'class': 'form-control', 'data-provide':'datepicker'}),
        }
