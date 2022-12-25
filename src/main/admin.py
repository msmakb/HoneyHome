from django.contrib.admin import ModelAdmin, register
from django.db.models.functions import Lower
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest

from .constants import BASE_MODEL_FIELDS, ROWS_PER_PAGE, ACCESS_TYPE
from .models import AuditEntry, BlockedClient, Parameter, Person
from .utils import setCreatedByUpdatedBy


@register(AuditEntry)
class AuditEntryAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('action', 'user_agent', 'username', 'ip',
                                     *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('action', 'created',)
    search_fields: tuple[str, ...] = ('action', 'user_agent', 'username', 'ip')
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def has_change_permission(self, *args, **kwargs) -> bool:
        return False


@register(BlockedClient)
class BlockedClientAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('user_agent', 'ip', 'block_type',
                                     'blocked_times', *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('created',)
    search_fields: tuple[str, ...] = ('user_agent', 'ip')
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def save_model(self, request: HttpRequest, obj: BlockedClient, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(Parameter)
class ParameterAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('parameter', 'value', 'description',
                                     *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('updated',)
    search_fields: tuple[str, ...] = ('name', 'value')
    ordering: tuple[str, ...] = ('name',)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def parameter(self, obj: Parameter) -> str:
        return obj.__str__()

    def get_queryset(self, request: HttpRequest) -> QuerySet[Parameter]:
        queryset: QuerySet[Parameter] = super().get_queryset(request)
        return queryset.filter(access_type=ACCESS_TYPE.ADMIN_ACCESS)

    def has_add_permission(self, *args, **kwargs) -> bool:
        return False

    def has_delete_permission(self, *args, **kwargs) -> bool:
        return False

    def save_model(self, request: HttpRequest, obj: Parameter, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(Person)
class PersonAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('name', 'gender',
                                     'nationality', 'date_of_birth',
                                     'address', 'contacting_email',
                                     'phone_number', *BASE_MODEL_FIELDS)
    list_filter: tuple[str, ...] = ('nationality', 'created')
    search_fields: tuple[str, ...] = ('name', )
    ordering: tuple[str, ...] = (Lower('name'),)
    list_per_page: int = ROWS_PER_PAGE
    exclude: tuple[str, ...] = BASE_MODEL_FIELDS

    def save_model(self, request: HttpRequest, obj: Person, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)
