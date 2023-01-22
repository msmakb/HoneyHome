from django_filters import FilterSet, CharFilter, ChoiceFilter, DateFromToRangeFilter
from django import forms

from accounting_manager.filters import DateRangeWidget

from .models import GoodsMovement

form_class: str = 'form-control form-control shadow-sm rounded'


class GoodsMovementFilter(FilterSet):
    item_choices: list[str, str] = []
    for goods in GoodsMovement.getAll():
        if (goods.item, goods.item) not in item_choices:
            item_choices.append((goods.item, goods.item))

    item = ChoiceFilter(
        field_name='item',
        lookup_expr='iexact',
        label='item',
        choices=item_choices,
        widget=forms.Select(
            attrs={
                'class': form_class,
            }
        )
    )
    sender = CharFilter(
        field_name='sender',
        lookup_expr='icontains',
        label='sender',
        widget=forms.TextInput(
            attrs={
                'class': form_class,
                'placeholder': 'sender',
            }
        )
    )
    receiver = CharFilter(
        field_name='receiver',
        lookup_expr='icontains',
        label='receiver',
        widget=forms.TextInput(
            attrs={
                'class': form_class,
                'placeholder': 'receiver',
            }
        )
    )
    created = DateFromToRangeFilter(
        field_name='created',
        lookup_expr='icontains',
        label='Date',
        widget=DateRangeWidget(
            from_attrs={
                'class': 'form-control',
                'data-provide': 'datepicker'
            },
            to_attrs={
                'class': 'form-control',
                'data-provide': 'datepicker'
            }
        )
    )

    class Meta:
        model = GoodsMovement
        fields = [
            'item',
            'sender',
            'receiver',
            'created',
        ]
