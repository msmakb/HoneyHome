from django.contrib import admin
from .models import Expenses, Sales


class ExpensesAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'quantity', 'price', 'date', 'note')

class SalesAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'batch', 'quantity', 'price', 'date', 'seller')

# Registering models in admen page
admin.site.register(Expenses, ExpensesAdmin)
admin.site.register(Sales, SalesAdmin)
