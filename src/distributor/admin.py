from django.contrib.admin import ModelAdmin, register
from main.constants import BASE_MODEL_FIELDS, ROWS_PER_PAGE
from main.utils import setCreatedByUpdatedBy
from .models import Distributor, SalesHistory


@register(Distributor)
class DistributorAdmin(ModelAdmin):
    list_display = ('id', 'name', 'account',
                    'stock', *BASE_MODEL_FIELDS)
    list_filter = ('created',)
    search_fields = ('person__name', 'account__username')
    list_per_page = ROWS_PER_PAGE
    exclude = BASE_MODEL_FIELDS

    def save_model(self, request, obj, form, change):
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)

    def name(self, obj):
        return obj.person.name


@register(SalesHistory)
class SalesHistoryAdmin(ModelAdmin):
    list_display = ('id', 'distributor', 'type', 'batch',
                    'quantity', 'price', 'receiving_date',
                    'received_from', 'payment_date',
                    *BASE_MODEL_FIELDS)
    list_filter = ('type', 'batch',
                   'received_from', 'created')
    search_fields = ('distributor__person__name',)
    list_per_page = ROWS_PER_PAGE
    exclude = BASE_MODEL_FIELDS

    def save_model(self, request, obj, form, change):
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)
