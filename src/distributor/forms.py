from django import forms
from django.forms import ModelForm
from warehouse_admin.models import ItemCard


class SendPaymentForm(ModelForm):
    def __init__(self, pk=1, *args, **kwargs):
        super(SendPaymentForm, self).__init__(*args, **kwargs)
        items, batches = [], []
        stock = ItemCard.objects.filter(stock=pk)
        for i in stock:
            if (f'{i.type}', f'{i.type}') not in items: 
                items.append((f'{i.type}', f'{i.type}'))
            if (f'{i.batch}', f'{i.batch}') not in batches: 
                batches.append((f'{i.batch}', f'{i.batch}'))
        widget = forms.Select(attrs={'required': True, 'class': 'form-control'})
        fileWidget = forms.FileInput(attrs={'required': True, 'class': 'form-control'})
        self.fields['type'] = forms.ChoiceField(choices=items, widget=widget)
        self.fields['batch'] = forms.ChoiceField(choices=batches, widget=widget)
        self.fields['receipt'] = forms.FileField(widget=fileWidget)

    class Meta:
        model = ItemCard
        fields = [
            'quantity',
        ]
        widgets = {
            'quantity': forms.NumberInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Quantity'}),
        }

