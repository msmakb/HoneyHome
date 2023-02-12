from typing import Any

from django import forms
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils import timezone

from main import constants
from main.forms import DateInput
from main.utils import clean_form_created_by, clean_form_updated_by

from .models import Batch, ItemCard, ItemType, RetailCard, RetailItem


class AddGoodsForm(ModelForm):

    def __init__(self, request: HttpRequest, *args, **kwargs) -> None:
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
            if batch.available_quantity <= 0:
                batch_choices_to_remove.append(choice)
            else:
                batch_choices[index] = (
                    batch_choices[index][0],
                    f"{batch_choices[index][1]} - available ({batch.available_quantity})")

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
            'created_by': forms.HiddenInput(attrs={'required': False}),
            'updated_by': forms.HiddenInput(attrs={'required': False}),
        }

    def save(self, commit: bool = ...) -> tuple[str, int]:
        cleaned_data: dict[str, Any] = self.cleaned_data
        type: ItemType = cleaned_data.get('type')
        batch: Batch = cleaned_data.get('batch')
        quantity: int = cleaned_data.get('quantity')
        received_from: str = cleaned_data.get('received_from')
        item_card: QuerySet[ItemCard] = ItemCard.filter(
            stock=constants.MAIN_STORAGE_ID,
            type=type,
            batch=batch,
            received_from=received_from,
            created__startswith=timezone.now().date())
        batch.setAvailableQuantity(
            self.request,
            batch.available_quantity - quantity
        )
        if item_card.exists():
            if len(item_card) == 1:
                item_card: ItemCard = item_card[0]
            else:
                item_card: ItemCard = ItemCard.orderFiltered(
                    'id', reverse=True, type=type, batch=batch,
                    received_from=received_from,
                    created__startswith=timezone.now().date())[0]
            item_card.setQuantity(self.request, item_card.quantity + quantity)
        else:
            super().save(commit)

        return (type.name, quantity)

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
        if batch.available_quantity - quantity < 0:
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
            'is_retail_child',
            'retail_child_of',
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
            'is_retail': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'onchange': 'toggleIsRetailChildCheckbox()'
                }
            ),
            'is_retail_child': forms.CheckboxInput(
                attrs={
                    'disabled': True,
                    'class': 'form-check-input',
                    'onchange': 'toggleIsRetailChildOfInput()'
                }
            ),
            'retail_child_of': forms.TextInput(
                attrs={
                    'disabled': True,
                    'class': 'form-control',
                    'placeholder': 'Parent Item Code',
                }
            ),
            'created_by': forms.HiddenInput(attrs={'required': False}),
            'updated_by': forms.HiddenInput(attrs={'required': False}),
        }

    def clean_weight(self) -> int:
        data = self.cleaned_data.get("weight")
        if data <= 0:
            raise forms.ValidationError(
                "Sorry, you must enter a positive number for the weight in grams.")

        return data

    def clean_code(self):
        code: str = self.cleaned_data.get("code")
        if " " in code:
            raise forms.ValidationError(
                "Sorry, item code must have no spaces in between.")

        return code.upper()

    def clean_retail_child_of(self):
        retail_child_of: str = self.cleaned_data.get("retail_child_of")
        if retail_child_of:
            return retail_child_of.upper()
        else:
            return retail_child_of

    def clean_created_by(self) -> str:
        object_str_representation: str = self.cleaned_data.get('name')
        return clean_form_created_by(self, object_str_representation)

    def clean_updated_by(self) -> str:
        return clean_form_updated_by(self)

    def clean(self) -> dict[str, Any]:
        cleaned_data: dict[str, Any] = super().clean()
        is_retail: bool = cleaned_data.get("is_retail")
        is_retail_child: bool = cleaned_data.get("is_retail_child")
        if is_retail and not is_retail_child:
            cleaned_data['weight'] = 0
            if 'weight' in self.errors:
                del self.errors['weight']

        if is_retail_child:
            retail_child_of = cleaned_data.get("retail_child_of")
            if not retail_child_of:
                self.add_error(
                    'retail_child_of',
                    "You must specify the item code of the parent."
                )
                return cleaned_data
            if not ItemType.isExists(
                code=retail_child_of,
                is_retail=True,
                is_retail_child=False,
            ):
                self.add_error(
                    'retail_child_of',
                    "Sorry, the parent item code dose not exist."
                )

        return cleaned_data


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
            'available_quantity',
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
            'available_quantity': forms.HiddenInput(attrs={'required': False}),
            'created_by': forms.HiddenInput(attrs={'required': False}),
            'updated_by': forms.HiddenInput(attrs={'required': False}),
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

    def clean(self) -> dict[str, Any]:
        if 'available_quantity' in self.errors:
            del self.errors['available_quantity']
        cleaned_data: dict[str, Any] = super().clean()
        cleaned_data['available_quantity'] = cleaned_data.get('quantity')
        return cleaned_data


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
            stock__id=stock_id,
            status=constants.ITEM_STATUS.GOOD,
            type__is_retail=False)
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
            'created_by': forms.HiddenInput(attrs={'required': False}),
            'updated_by': forms.HiddenInput(attrs={'required': False}),
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
                    "The quantity of the specified item and batch is not available in the stock")

        return quantity

    def clean_created_by(self) -> str:
        object_str_representation: str = self.cleaned_data.get('name')
        return clean_form_created_by(self, object_str_representation)

    def clean_updated_by(self) -> str:
        return clean_form_updated_by(self)


class AddDamagedGoodsForm(forms.ModelForm):

    def __init__(self, request: HttpRequest, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not isinstance(request, HttpRequest):
            raise TypeError("Invalid request object!")
        self.request: HttpRequest = request

        item_type_choices: list[tuple] = list(self.fields['type'].choices)
        batch_choices: list[tuple] = list(self.fields['batch'].choices)
        item_type_choices_to_remove: list[tuple] = []
        batch_choices_to_remove: list[tuple] = []

        self.available_types: dict[str: int] = {}
        item_cards: QuerySet[ItemCard] = ItemCard.filter(
            stock__id=constants.MAIN_STORAGE_ID,
            status=constants.ITEM_STATUS.GOOD,
            type__is_retail=False)
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

        available_batch: list[Batch] = [
            item.batch.name for item in ItemCard.filter(
                stock__id=constants.MAIN_STORAGE_ID,
                status=constants.ITEM_STATUS.GOOD,
                type__is_retail=False)]

        for index, choice in enumerate(batch_choices):
            if index == 0:
                continue
            if choice[1] not in available_batch:
                batch_choices_to_remove.append(choice)

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
            'quantity',
            'batch',
            'received_from',
            'note',
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
            'batch': forms.Select(
                attrs={
                    'required': True,
                    'class': 'form-control'
                }
            ),
            'received_from': forms.TextInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Received From'
                }
            ),
            'note': forms.Textarea(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Description'
                }
            ),
            'created_by': forms.HiddenInput(attrs={'required': False}),
            'updated_by': forms.HiddenInput(attrs={'required': False}),
        }

    def clean_type(self) -> ItemType:
        item_type: ItemType = self.cleaned_data.get("type")
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

    def clean_batch(self) -> Batch:
        batch: Batch = self.cleaned_data.get("batch")
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
        quantity = self.cleaned_data.get("quantity")
        if quantity <= 0:
            raise forms.ValidationError(
                "Sorry, you must enter a positive number more than 0 for the quantity.")

        return quantity

    def clean_created_by(self) -> str:
        object_str_representation: str = self.cleaned_data.get('name')
        return clean_form_created_by(self, object_str_representation)

    def clean_updated_by(self) -> str:
        return clean_form_updated_by(self)

    def clean(self) -> dict[str, Any]:
        cleaned_data: dict[str, Any] = super().clean()
        item_type: ItemType = cleaned_data.get("type")
        batch: Batch = cleaned_data.get("batch")
        quantity: int = cleaned_data.get("quantity")

        if item_type is not None:
            items: QuerySet[ItemCard] = ItemCard.filter(
                stock__id=constants.MAIN_STORAGE_ID,
                type=item_type,
                batch=batch,
                status=constants.ITEM_STATUS.GOOD)
            if not items.exists():
                self.add_error('batch', forms.ValidationError(
                    "Sorry, the selected batch in main storage does not contain this type of item."))
            if sum([item.quantity for item in items]) < quantity:
                self.add_error('quantity', forms.ValidationError(
                    "Sorry, the specified quantity of the item for the selected batch is not available in the current stock."))

        return cleaned_data


class ConvertToRetailForm(ModelForm):

    from_type = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'required': True,
                'class': 'form-control'
            }
        ),
    )
    quantity = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                'required': True,
                'class': 'form-control',
                'placeholder': 'Quantity'
            }
        ),
    )

    class Meta:
        model = RetailCard
        fields = [
            'type',
            'weight',
            'created_by',
            'updated_by',
        ]
        widgets = {
            'type': forms.Select(
                attrs={
                    'required': True,
                    'class': 'form-control'
                }
            ),
            'weight': forms.NumberInput(
                attrs={
                    'required': True,
                    'class': 'form-control',
                    'placeholder': 'Total Weight'
                }
            ),
            'created_by': forms.HiddenInput(attrs={'required': False}),
            'updated_by': forms.HiddenInput(attrs={'required': False}),
        }

    def __init__(self, request: HttpRequest, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not isinstance(request, HttpRequest):
            raise TypeError("Invalid request object!")
        self.request: HttpRequest = request

        self.available_from_types: dict[ItemType: int] = {}
        available_to_types: QuerySet[ItemType] = ItemType.filter(
            is_retail=True, is_retail_child=False)
        from_type_choices: list[tuple] = [('', '---------')]
        to_type_choices: list[tuple] = list(self.fields['type'].choices)
        choices_to_remove: list[tuple] = []

        for choice in to_type_choices:
            if not choice[0]:
                continue
            if choice[0].instance not in available_to_types:
                choices_to_remove.append(choice)

        for choice in choices_to_remove:
            to_type_choices.remove(choice)

        item_cards: QuerySet[ItemCard] = ItemCard.orderFiltered(
            'type__name',
            stock__id=constants.MAIN_STORAGE_ID,
            type__is_retail=False)

        if item_cards.exists():
            for item in item_cards:
                if item.type in self.available_from_types:
                    self.available_from_types[item.type] += item.quantity
                else:
                    self.available_from_types[item.type] = item.quantity

        for item, quantity in self.available_from_types.items():
            from_type_choices.append(
                (item, f"{item.name} - available ({quantity})")
            )

        # # update choices
        self.fields['from_type'].choices = from_type_choices
        self.fields['from_type'].widget.choices = from_type_choices
        self.fields['type'].choices = to_type_choices
        self.fields['type'].widget.choices = to_type_choices

    def save(self, commit: bool = ...) -> Any:
        item_type = self.cleaned_data.get("type")
        weight = self.cleaned_data.get("weight")
        updated_by = self.cleaned_data.get("updated_by")
        try:
            retail_card: RetailCard = RetailCard.get(type=item_type)
            retail_card.weight += weight
            retail_card.updated_by = updated_by
            retail_card.save()
        except RetailCard.DoesNotExist:
            if weight == 0:
                return
            return super().save(commit)

    def clean_from_type(self):
        from_type: ItemType = ItemType.get(
            name=self.cleaned_data.get("from_type"))
        if from_type not in self.available_from_types:
            raise forms.ValidationError(
                "Select a valid choice. That choice is not one of the available choices.")

        return from_type

    def clean_type(self):
        item_type: ItemType = self.cleaned_data.get("type")
        if not item_type.is_retail or item_type.is_retail_child:
            raise forms.ValidationError(
                "Select a valid choice. That choice is not one of the available choices.")

        return item_type

    def clean_created_by(self) -> str:
        object_str_representation: str = self.cleaned_data.get('name')
        return clean_form_created_by(self, object_str_representation)

    def clean_updated_by(self) -> str:
        return clean_form_updated_by(self)

    def clean(self) -> dict[str, Any]:
        cleaned_date: dict[str, Any] = super().clean()
        from_type: ItemType = ItemType.get(name=cleaned_date.get('from_type'))
        quantity: int = int(cleaned_date.get('quantity'))
        weight: int = int(cleaned_date.get('weight'))
        if weight == 0:
            damaged_items: QuerySet[ItemCard] = ItemCard.filter(
                type=from_type,
                stock__id=constants.MAIN_STORAGE_ID,
                status=constants.ITEM_STATUS.DAMAGED
            )

            if damaged_items.exists():
                count: int = 0
                for damaged_item in damaged_items:
                    count += damaged_item.quantity
                if quantity > count:
                    self.add_error(
                        'quantity',
                        'Sorry, the specified quantity as damaged goods is not recorded in the system'
                    )
                    return cleaned_date

                self.add_error(
                    'weight',
                    'The system is unable to process the request as there are no damaged goods recorded. '
                    + 'Please provide the weight to continue.'
                )

        items: QuerySet[ItemCard] = ItemCard.filter(
            type=from_type,
            stock__id=constants.MAIN_STORAGE_ID,
        )
        count = 0
        for item in items:
            count += item.quantity

        if quantity > count:
            self.add_error(
                'quantity',
                'The quantity of the specified item is not available in the stock'
            )

        return cleaned_date


class AddRetailGoodsForm(ModelForm):

    class Meta:
        model = RetailItem
        fields = [
            'type',
            'quantity',
        ]
        widgets = {
            'type': forms.Select(
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
            'created_by': forms.HiddenInput(attrs={'required': False}),
            'updated_by': forms.HiddenInput(attrs={'required': False}),
        }

    def __init__(self, request: HttpRequest, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not isinstance(request, HttpRequest):
            raise TypeError("Invalid request object!")
        self.request: HttpRequest = request

        item_type_choices: list[tuple] = list(self.fields['type'].choices)
        self.available_item_types: list[ItemType] = []
        choices_to_remove: list[tuple] = []

        retail_cards: QuerySet[RetailCard] = RetailCard.getAll()
        for retail_card in retail_cards:
            item_types: QuerySet[ItemType] = ItemType.filter(
                is_retail=True,
                is_retail_child=True,
                retail_child_of=retail_card.type.code
            )
            for item_type in item_types:
                self.available_item_types.append(item_type)

        for choice in item_type_choices:
            if not choice[0]:
                continue
            if choice[0].instance not in self.available_item_types:
                choices_to_remove.append(choice)

        for choice in choices_to_remove:
            item_type_choices.remove(choice)

        self.fields['type'].choices = item_type_choices
        self.fields['type'].widget.choices = item_type_choices

    def save(self, commit: bool = ...) -> Any:
        cleaned_data: dict[str, Any] = self.cleaned_data
        item_type: ItemType = cleaned_data.get('type')
        quantity: int = cleaned_data.get('quantity')
        total_weight: int = item_type.weight * quantity
        retail_card: RetailCard = RetailCard.get(
            type__code=item_type.retail_child_of)
        if retail_card.weight < total_weight:
            from main.messages import SOMETHING_WRONG
            SOMETHING_WRONG(self.request)
            return
        if retail_card.weight == retail_card:
            retail_card.delete(self.request)
        else:
            retail_card.setWeight(
                self.request,
                retail_card.weight - total_weight
            )

        try:
            retail_item: RetailItem = RetailItem.get(type=item_type)
            retail_item.setQuantity(
                self.request,
                retail_item.quantity + quantity
            )
        except RetailItem.DoesNotExist:
            return super().save(commit)

    def clean_type(self):
        item_type: ItemType = self.cleaned_data.get("type")
        if item_type not in self.available_item_types:
            raise forms.ValidationError(
                "Select a valid choice. That choice is not one of the available choices.")

        return item_type

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity <= 0:
            raise forms.ValidationError(
                "Sorry, you must enter a positive number more than 0 for the quantity.")

        return quantity

    def clean_created_by(self) -> str:
        object_str_representation: str = self.cleaned_data.get('name')
        return clean_form_created_by(self, object_str_representation)

    def clean_updated_by(self) -> str:
        return clean_form_updated_by(self)

    def clean(self) -> dict[str, Any]:
        cleaned_data: dict[str, Any] = super().clean()
        item_type: ItemType = cleaned_data.get('type')
        quantity: int = cleaned_data.get('quantity')
        try:
            retail_card: RetailCard = RetailCard.get(
                type__code=item_type.retail_child_of)
            if retail_card.weight < (item_type.weight * quantity):
                self.add_error(
                    'quantity',
                    'Sorry, the specified quantity is not available in the converted retail.'
                )

        except (RetailCard.DoesNotExist, AttributeError):
            self.add_error(
                'type',
                'Select a valid choice. That choice is not one of the available choices.'
            )

        return cleaned_data
