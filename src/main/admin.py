from django.contrib import admin
from .models import Person


class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'gender', 
                    'nationality', 'date_of_birth', 
                    'address', 'contacting_email',
                    'phone_number', 'register_date')

admin.site.register(Person, PersonAdmin)
