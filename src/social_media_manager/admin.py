from django.contrib import admin
from .models import Customer, CustomerPurchase, Questionnaire


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'person', 'instagram', 'shopee', 'facebook')

class CustomerPurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'item', 'quantity', 'Purchase_from')

class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description',
                    'numbers_of_questions', 'numbers_of_replies',
                    'period', 'creation_date', 'end_date')

# Register your models here.
admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerPurchase, CustomerPurchaseAdmin)
admin.site.register(Questionnaire, QuestionnaireAdmin)

