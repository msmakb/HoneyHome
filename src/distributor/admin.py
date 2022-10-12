from django.contrib import admin
from .models import Distributor, SalesHistory


class DistributorAdmin(admin.ModelAdmin):
    list_display = ('id', 'person', 'account', 'stock')

class SalesHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'distributor', 'type', 'batch', 
                    'quantity', 'price', 'receiving_date', 
                    'received_from', 'payment_date')
                    
# Register your models here.
admin.site.register(Distributor, DistributorAdmin)
admin.site.register(SalesHistory, SalesHistoryAdmin)
