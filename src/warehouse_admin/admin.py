from django.contrib.admin import ModelAdmin, register
from main.constants import BASE_MODEL_FIELDS, MAIN_STORAGE_ID
from .models import Batch, ItemType, ItemCard, RetailItem, RetailCard, Stock, GoodsMovement


@register(Batch)
class BatchAdmin(ModelAdmin):
    list_display = ('id', 'name', 'code', 'arrival_date',
                    'quantity', 'description', *BASE_MODEL_FIELDS)
    list_filter = ('arrival_date', 'created')


@register(ItemType)
class ItemTypeAdmin(ModelAdmin):
    list_display = ('id', 'name', 'code', 'weight',
                    'is_retail', *BASE_MODEL_FIELDS)
    list_filter = ('weight', 'is_retail', 'created')


@register(ItemCard)
class ItemCardAdmin(ModelAdmin):
    list_display = ('id', 'type', 'batch', 'stock',
                    'quantity', 'status', 'price',
                    'receiving_date', 'received_from',
                    'is_transforming', 'is_priced',
                    *BASE_MODEL_FIELDS)
    list_filter = ('type', 'batch', 'stock', 'status',
                   'is_transforming', 'is_priced', 'created')


@register(GoodsMovement)
class GoodsMovementAdmin(ModelAdmin):
    list_display = ('id', 'item', 'sender', 'receiver',
                    'date', *BASE_MODEL_FIELDS)
    list_filter = ('item', 'sender', 'receiver',
                   'date', 'created')


@register(RetailCard)
class RetailCardAdmin(ModelAdmin):
    list_display = ('id', 'type', 'conversion_date',
                    'weight', *BASE_MODEL_FIELDS)
    list_filter = ('type', 'weight', 'created')


@register(RetailItem)
class RetailItemAdmin(ModelAdmin):
    list_display = ('id', 'type', 'quantity',
                    'price', *BASE_MODEL_FIELDS)
    list_filter = ('type', 'created')


@register(Stock)
class StockAdmin(ModelAdmin):
    list_display = ('id', 'stock_owner', *BASE_MODEL_FIELDS)
    list_filter = ('created',)

    def stock_owner(self, obj):
        stock: str = ''
        if obj.id == MAIN_STORAGE_ID:
            stock = 'Main Storage Stock'
        else:
            from distributor.models import Distributor
            distributor = Distributor.get(stock=obj.id)
            person = distributor.getPerson
            stock = person.getName
        return stock
