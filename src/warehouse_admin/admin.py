from django.contrib.admin import ModelAdmin, register
from django.db.models.functions import Lower
from django.forms import ModelForm
from django.http import HttpRequest

from main.constants import BASE_MODEL_FIELDS, MAIN_STORAGE_ID, ROWS_PER_PAGE
from main.models import Person
from main.utils import setCreatedByUpdatedBy

from .models import (Batch, GoodsMovement, ItemCard, ItemType, RetailCard,
                     RetailItem, Stock)


@register(Batch)
class BatchAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('name', 'code', 'arrival_date',
                                     'quantity', 'description', *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('arrival_date', 'created')
    search_fields: tuple[str, ...] = ('name', 'code', 'arrival_date')
    ordering: tuple[str, ...] = ('arrival_date', 'created')
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def delete_model(self, request: HttpRequest, obj: Batch) -> None:
        return obj.delete(request)

    def save_model(self, request: HttpRequest, obj: Batch, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(ItemType)
class ItemTypeAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('name', 'code', 'weight',
                                     'is_retail', *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('weight', 'weight', 'is_retail',
                                    'created')
    search_fields: tuple[str, ...] = ('name', 'code',)
    ordering: tuple[str, ...] = (Lower('name'), 'code',)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def delete_model(self, request: HttpRequest, obj: ItemType) -> None:
        return obj.delete(request)

    def save_model(self, request: HttpRequest, obj: ItemType, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(ItemCard)
class ItemCardAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('type', 'batch', 'stock',
                                     'quantity', 'status', 'price',
                                     'receiving_date', 'received_from',
                                     'is_transforming', 'is_priced',
                                     *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('type', 'batch', 'stock', 'status',
                                    'is_transforming', 'is_priced', 'created')
    search_fields: tuple[str, ...] = ('type__name', 'batch__name', 'created',
                                      'received_from')
    ordering: tuple[str, ...] = ('created', 'received_from',
                                 Lower('type__name'), Lower('batch__name'), )
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def receiving_date(self, obj: ItemCard):
        return obj.receiving_date

    def delete_model(self, request: HttpRequest, obj: ItemCard) -> None:
        return obj.delete(request)

    def save_model(self, request: HttpRequest, obj: ItemCard, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(GoodsMovement)
class GoodsMovementAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('item', 'code', 'batch', 'quantity', 'status',
                                     'sender', 'receiver', 'date', *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('item', 'sender', 'receiver',
                                    'created')
    search_fields: tuple[str, ...] = ('item__type__name', 'created',
                                      'sender', 'receiver')
    ordering: tuple[str, ...] = (Lower('item'), Lower('sender'),
                                 Lower('receiver'))
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def date(self, obj: GoodsMovement) -> str:
        return obj.date

    def delete_model(self, request: HttpRequest, obj: GoodsMovement) -> None:
        return obj.delete(request)

    def save_model(self, request: HttpRequest, obj: GoodsMovement, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(RetailCard)
class RetailCardAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('type', 'weight',
                                     *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('type', 'created')
    search_fields: tuple[str, ...] = (Lower('type__name'),)
    ordering: tuple[str, ...] = ('created', Lower('type__name'),
                                 'weight')
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def delete_model(self, request: HttpRequest, obj: RetailCard) -> None:
        return obj.delete(request)

    def save_model(self, request: HttpRequest, obj: RetailCard, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(RetailItem)
class RetailItemAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('type', 'quantity',
                                     'price', *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('type', 'created')
    search_fields: tuple[str, ...] = (Lower('type__name'),)
    ordering: tuple[str, ...] = (Lower('type__name'),)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def delete_model(self, request: HttpRequest, obj: RetailItem) -> None:
        return obj.delete(request)

    def save_model(self, request: HttpRequest, obj: RetailItem, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(Stock)
class StockAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('stock_owner', *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('created',)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def has_change_permission(self, *args, **kwargs) -> bool:
        return False

    def delete_model(self, request: HttpRequest, obj: Stock) -> None:
        return obj.delete(request)

    def save_model(self, request: HttpRequest, obj: Stock, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)

    def stock_owner(self, obj: Stock):
        stock_own: str = ''
        if obj.id == MAIN_STORAGE_ID:
            stock_own = 'Main Storage Stock'
        else:
            from distributor.models import Distributor
            distributor: Distributor = Distributor.get(stock=obj.id)
            person: Person = distributor.person
            stock_own = person.name
        return stock_own
