from django.contrib.admin import ModelAdmin, register
from django.db.models.functions import Lower
from django.forms import ModelForm
from django.http import HttpRequest

from .constants import BASE_MODEL_FIELDS, PARAMETERS, ROWS_PER_PAGE
from .models import AuditEntry, BlockedClient, Parameter, Person
from .utils import setCreatedByUpdatedBy


@register(AuditEntry)
class AuditEntryAdmin(ModelAdmin):
    list_display = ('action', 'user_agent', 'username', 'ip',
                    *BASE_MODEL_FIELDS)
    list_filter = ('action', 'created',)
    search_fields = ('action', 'user_agent', 'username', 'ip')
    list_per_page = ROWS_PER_PAGE
    exclude = BASE_MODEL_FIELDS

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def has_change_permission(self, *args, **kwargs) -> bool:
        return False


@register(BlockedClient)
class BlockedClientAdmin(ModelAdmin):
    list_display = ('user_agent', 'ip', 'block_type',
                    'blocked_times', *BASE_MODEL_FIELDS)
    list_filter = ('created',)
    search_fields = ('user_agent', 'ip')
    list_per_page = ROWS_PER_PAGE
    exclude = BASE_MODEL_FIELDS

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def save_model(self, request: HttpRequest, obj: BlockedClient, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(Parameter)
class ParameterAdmin(ModelAdmin):
    list_display = ('parameter', 'value', 'description',
                    *BASE_MODEL_FIELDS)
    list_filter = ('updated',)
    search_fields = ('name', 'value')
    ordering = ('name',)
    list_per_page = ROWS_PER_PAGE
    exclude = BASE_MODEL_FIELDS

    def parameter(self, obj: Parameter) -> str:
        return obj.getName.replace('_', ' ').capitalize()

    def get_queryset(self, request: HttpRequest):
        EXCLUDED_PARAMETERS: list = [PARAMETERS.MAGIC_NUMBER]
        queryset = super().get_queryset(request)
        return queryset.exclude(name__in=EXCLUDED_PARAMETERS)

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def has_delete_permission(self, *args, **kwargs) -> bool:
        return False

    def save_model(self, request: HttpRequest, obj: Parameter, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(Person)
class PersonAdmin(ModelAdmin):
    list_display = ('name', 'gender',
                    'nationality', 'date_of_birth',
                    'address', 'contacting_email',
                    'phone_number', *BASE_MODEL_FIELDS)
    list_filter = ('nationality', 'created')
    search_fields = ('name', )
    ordering = (Lower('name'),)
    list_per_page = ROWS_PER_PAGE
    exclude = BASE_MODEL_FIELDS

    def save_model(self, request: HttpRequest, obj: Person, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)
