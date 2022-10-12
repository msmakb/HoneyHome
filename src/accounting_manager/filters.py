import django_filters
from django import forms
from django.db.utils import OperationalError
from .models import Sales

class DateInput(forms.DateInput):
    input_type = 'date'

class DateRangeWidget(django_filters.widgets.DateRangeWidget):

    def __init__(self, from_attrs=None, to_attrs=None, attrs=None):
        super(DateRangeWidget, self).__init__(attrs)
        self.widgets[0].input_type = 'date'
        self.widgets[1].input_type = 'date'
        
        if from_attrs:
            self.widgets[0].attrs.update(from_attrs)
        if to_attrs:
            self.widgets[1].attrs.update(to_attrs)

def getChoises():
    items, batches, sellers = [], [], []
    sales = Sales.objects.filter(is_approved=True)
    try:
        for i in sales:
            if (f'{i.type}', f'{i.type}') not in items: 
                items.append((i.type.id, f'{i.type}'))
            if (f'{i.batch}', f'{i.batch}') not in batches: 
                batches.append((i.batch.id, f'{i.batch}'))
            if (f'{i.seller}', f'{i.seller}') not in sellers: 
                sellers.append((f'{i.seller}', f'{i.seller}'))
    except OperationalError: pass
    return {'items': items, 'batches': batches, 'sellers': sellers}

class SalesFilter(django_filters.FilterSet):
    type = django_filters.ChoiceFilter(
        choices= getChoises()['items'],
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Type'}))
    batch = django_filters.ChoiceFilter(
        choices= getChoises()['batches'],
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Batch'}))
    seller = django_filters.ChoiceFilter(
        choices= getChoises()['sellers'],
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Seller'}))
    date = django_filters.DateFromToRangeFilter(
        widget=DateRangeWidget(
            from_attrs={'class': 'form-control', 'data-provide':'datepicker'},
            to_attrs={'class': 'form-control', 'data-provide':'datepicker'}))


    class Meta:
        model = Sales
        fields = [
            'type',
            'batch',
            'seller',
            'date',
        ]
