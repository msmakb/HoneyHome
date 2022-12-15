from django import forms
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest

from main.forms import DateInput
from main.utils import clean_form_created_by, clean_form_updated_by

from .models import Batch, ItemCard, ItemType, RetailItem


class AddGoodsForm(ModelForm):

    def __init__(self, request: HttpRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(request, HttpRequest):
            raise TypeError("Invalid request object!")
        self.request: HttpRequest = request

        item_type_choices: list[tuple] = list(self.fields['type'].choices)
        batch_choices: list[tuple] = list(self.fields['batch'].choices)
        item_type_choices_to_remove: list[tuple] = []
        batch_choices_to_remove: list[tuple] = []

        for index, choice in enumerate(batch_choices):
            if index == 0:
                continue
            batch: Batch = Batch.get(name=choice[1])
            if batch.getAvailableQuantity() <= 0:
                batch_choices_to_remove.append(choice)
            else:
                batch_choices[index] = (
                    batch_choices[index][0],
                    f"{batch_choices[index][1]} - available ({batch.getAvailableQuantity()})")

        not_retail_type: list[int] = [i.id for i in ItemType.objects.filter(
            is_retail=False)]
        for choice in item_type_choices:
            if not choice[0]:
                continue
            elif choice[0] not in not_retail_type:
                item_type_choices_to_remove.append(choice)

        for choice in item_type_choices_to_remove:
            item_type_choices.remove(choice)
        for choice in batch_choices_to_remove:
            batch_choices.remove(choice)

        # update choices
        self.fields['type'].choices = item_type_choices
        self.fields['type'].widget.choices = item_type_choices
        self.fields['batch'].choices = batch_choices
        self.fields['batch'].widget.choices = batch_choices

    class Meta:
        model = ItemCard
        fields = [
            'type',
            'batch',
            'stock',
            'quantity',
            'received_from',
            'created_by',
            'updated_by',
        ]
        widgets = {
            'type': forms.Select(
                attrs={'required': True,
                       'class': 'form-control'
                       }
            ),
            'batch': forms.Select(
                attrs={
                    'required': True,
                    'class': 'form-control'
                }
            ),
            'quantity': forms.NumberInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Quantity'
                }
            ),
            'received_from': forms.TextInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Received From'
                }
            ),
        }

    def clean_type(self) -> ItemType:
        item_type: ItemType = self.cleaned_data["type"]
        item_type_choices: list[tuple] = list(self.fields['type'].choices)
        type_name: str = item_type.name
        clean: bool = False
        for choice in item_type_choices:
            if type_name == choice[1]:
                clean = True
                break
        if not clean:
            raise forms.ValidationError(
                "Select a valid choice. That choice is not one of the available choices.")
        return item_type

    def clean_batch(self) -> Batch:
        batch: Batch = self.cleaned_data["batch"]
        batch_choices: list[tuple] = list(self.fields['batch'].choices)
        batch_name: str = batch.name
        clean: bool = False
        for choice in batch_choices:
            if batch_name == str(choice[1].split(' - available ')[0]):
                clean = True
                break
        if not clean:
            raise forms.ValidationError(
                "Select a valid choice. That choice is not one of the available choices.")
        return batch

    def clean_quantity(self) -> int:
        batch: Batch = self.cleaned_data.get("batch")
        quantity: int = self.cleaned_data["quantity"]
        if batch is None:
            raise forms.ValidationError(
                "Select a valid choice. That choice is not one of the available choices.")
        if quantity <= 0:
            raise forms.ValidationError(
                "Not a valid quantity, Please add more than zero.")
        if batch.getAvailableQuantity() - quantity < 0:
            raise forms.ValidationError(
                "You passed the available quantity to add.")

        return quantity

    def clean_created_by(self) -> str:
        item_type: ItemType = self.cleaned_data.get('type')
        batch: Batch = self.cleaned_data.get('batch')
        if item_type is not None and batch is not None:
            object_str_representation: str = f"{item_type.name}-{batch.name}"
            return clean_form_created_by(self, object_str_representation)

    def clean_updated_by(self) -> str:
        return clean_form_updated_by(self)


class RegisterItemForm(ModelForm):

    def __init__(self, request: HttpRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(request, HttpRequest):
            raise TypeError("Invalid request object!")
        self.request: HttpRequest = request

    class Meta:
        model = ItemType
        fields = [
            'name',
            'code',
            'weight',
            'is_retail',
            'created_by',
            'updated_by',
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Name'
                }
            ),
            'code': forms.TextInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Code'
                }
            ),
            'weight': forms.NumberInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': '0 grams'
                }
            ),
            'is_retail': forms.CheckboxInput()
        }

    def clean_weight(self) -> int:
        data = self.cleaned_data["weight"]
        if data <= 0:
            raise forms.ValidationError(
                "Sorry, you must enter a positive number for the weight in grams.")

        return data

    def clean_created_by(self) -> str:
        object_str_representation: str = self.cleaned_data.get('name')
        return clean_form_created_by(self, object_str_representation)

    def clean_updated_by(self) -> str:
        return clean_form_updated_by(self)


class AddBatchForm(ModelForm):

    def __init__(self, request: HttpRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(request, HttpRequest):
            raise TypeError("Invalid request object!")
        self.request: HttpRequest = request

    class Meta:
        model = Batch
        fields = [
            'name',
            'code',
            'arrival_date',
            'quantity',
            'description',
            'created_by',
            'updated_by',
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Name'
                }
            ),
            'code': forms.TextInput(
                attrs={
                    'required': False,
                    'class': 'form-control',
                    'placeholder': 'Code'
                }
            ),
            'arrival_date': DateInput(
                attrs={
                    'required': False,
                    'class': 'form-control',
                    'data-provide': 'datepicker'
                }
            ),
            'quantity': forms.NumberInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Quantity'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'required': False,
                    'class': 'form-control',
                    'placeholder': 'Description'
                }
            ),
        }

    def clean_quantity(self) -> int:
        data = self.cleaned_data["quantity"]
        if data <= 0:
            raise forms.ValidationError(
                "Sorry, you must enter a positive number more than 0 for the quantity.")

        return data

    def clean_created_by(self) -> str:
        object_str_representation: str = self.cleaned_data.get('name')
        return clean_form_created_by(self, object_str_representation)

    def clean_updated_by(self) -> str:
        return clean_form_updated_by(self)


class SendGoodsForm(ModelForm):

    def __init__(self, request: HttpRequest, stock_id: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not isinstance(request, HttpRequest):
            raise TypeError("Invalid request object!")
        self.request: HttpRequest = request
        self.available_types: dict[str: int] = {}

        item_type_choices: list[tuple] = list(self.fields['type'].choices)
        item_type_choices_to_remove: list[tuple] = []

        item_cards: QuerySet[ItemCard] = ItemCard.filter(
            stock__id=stock_id, type__is_retail=False)
        if item_cards.exists():
            for item in item_cards:
                if item.type.name in self.available_types:
                    self.available_types[item.type.name] += item.quantity
                else:
                    self.available_types[item.type.name] = item.quantity

        for index, choice in enumerate(item_type_choices):
            if index == 0:
                continue
            item_types: ItemType = ItemType.get(name=choice[1])
            if item_types.name in self.available_types:
                item_type_choices[index] = (
                    item_type_choices[index][0],
                    f"{item_type_choices[index][1]} - available ({self.available_types.get(choice[1])})")
            else:
                item_type_choices_to_remove.append(choice)

        for choice in item_type_choices_to_remove:
            item_type_choices.remove(choice)

        # update choices
        self.fields['type'].choices = item_type_choices
        self.fields['type'].widget.choices = item_type_choices

    class Meta:
        model = ItemCard
        fields = [
            'type',
            'quantity',
            'created_by',
            'updated_by',
        ]
        widgets = {
            'type': forms.Select(
                attrs={'required': True,
                       'class': 'form-control'
                       }
            ),
            'quantity': forms.NumberInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Quantity'
                }
            ),
        }

    def clean_type(self) -> ItemType:
        item_type: ItemType = self.cleaned_data["type"]
        item_type_choices: list[tuple] = list(self.fields['type'].choices)
        item_type_name: str = item_type.name
        clean: bool = False
        for choice in item_type_choices:
            if item_type_name == str(choice[1].split(' - available ')[0]):
                clean = True
                break
        if not clean:
            raise forms.ValidationError(
                "Select a valid choice. That choice is not one of the available choices.")
        return item_type

    def clean_quantity(self) -> int:
        item_type: ItemType = self.cleaned_data.get("type")
        quantity = self.cleaned_data.get("quantity")
        if quantity <= 0:
            raise forms.ValidationError(
                "Sorry, you must enter a positive number more than 0 for the quantity.")
        if item_type is not None:
            if self.available_types.get(item_type.name) < quantity:
                raise forms.ValidationError(
                    "The specified quantity is not available in the stock")

        return quantity

    def clean_created_by(self) -> str:
        object_str_representation: str = self.cleaned_data.get('name')
        return clean_form_created_by(self, object_str_representation)

    def clean_updated_by(self) -> str:
        return clean_form_updated_by(self)


class ConvertToRetailForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ConvertToRetailForm, self).__init__(*args, **kwargs)
        items, batches = [], []
        stock = ItemCard.objects.filter(stock=1)
        for i in stock:
            if not i.type.is_retail and (f'{i.type}', f'{i.type}') not in items:
                items.append((f'{i.type}', f'{i.type}'))
            if (f'{i.batch}', f'{i.batch}') not in batches:
                batches.append((f'{i.batch}', f'{i.batch}'))
        widget = forms.Select(
            attrs={'required': True,
                   'class': 'form-control'
                   })
        self.fields['type'] = forms.ChoiceField(choices=items, widget=widget)
        self.fields['batch'] = forms.ChoiceField(
            choices=batches, widget=widget)

    class Meta:
        model = ItemCard
        fields = [
            'quantity',
        ]
        widgets = {
            'quantity': forms.NumberInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Quantity'
                }
            ),
        }


class AddRetailGoodsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(AddRetailGoodsForm, self).__init__(*args, **kwargs)

        types = []
        ItemTypes = ItemType.objects.filter(is_retail=True)
        for i in ItemTypes:
            types.append((f'{i}', f'{i}'))

        widget = forms.Select(
            attrs={'required': True,
                   'class': 'form-control'
                   })
        self.fields['type'] = forms.ChoiceField(choices=types, widget=widget)

    class Meta:
        model = RetailItem
        fields = [
            'quantity',
        ]
        widgets = {
            'quantity': forms.NumberInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Quantity'
                }
            ),
        }
