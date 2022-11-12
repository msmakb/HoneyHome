from django.contrib.admin import ModelAdmin, register
from django.db.models.functions import Lower
from django.forms import ModelForm
from django.http import HttpRequest
from django import forms
from main.constants import BASE_MODEL_FIELDS, ROWS_PER_PAGE
from main.utils import setCreatedByUpdatedBy

from .models import Employee, Task, TaskRate, Week, WeeklyRate


@register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ('name', 'account',
                    'position', *BASE_MODEL_FIELDS)
    list_filter = ('created',)
    search_fields = ('person__name', 'account__username')
    ordering = (Lower('person__name'),)
    list_per_page = ROWS_PER_PAGE
    exclude = BASE_MODEL_FIELDS

    def name(self, obj: Employee) -> str:
        return obj.person.name

    def save_model(self, request: HttpRequest, obj: Employee, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ('employee', 'task', 'description',
                    'status', 'receiving_date', 'deadline_date',
                    'time_left', 'submission_date', 'is_rated',
                    *BASE_MODEL_FIELDS)
    list_filter = ('status', 'is_rated', 'created')
    search_fields = ('employee__person__name', 'description')
    ordering = ('-updated',)
    list_per_page = ROWS_PER_PAGE
    exclude = BASE_MODEL_FIELDS

    def save_model(self, request: HttpRequest, obj: Task, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(TaskRate)
class TaskRateAdmin(ModelAdmin):
    list_display = ('id', 'task', 'on_time_rate',
                    'rate', *BASE_MODEL_FIELDS)
    list_filter = ('created',)
    search_fields = ('task__name',)
    ordering = ('created',)
    list_per_page = ROWS_PER_PAGE
    exclude = BASE_MODEL_FIELDS

    def save_model(self, request: HttpRequest, obj: TaskRate, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(Week)
class WeekAdmin(ModelAdmin):
    list_display = ('id', 'week_start_date', 'week_end_date',
                    'is_rated', *BASE_MODEL_FIELDS)
    list_filter = ('is_rated', 'created')
    search_fields = ('week_start_date', 'week_end_date')
    ordering = ('created',)
    list_per_page = ROWS_PER_PAGE
    exclude = BASE_MODEL_FIELDS

    def save_model(self, request: HttpRequest, obj: Week, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)


@register(WeeklyRate)
class WeeklyRateAdmin(ModelAdmin):
    list_display = ('id', 'week', 'employee',
                    'rate', *BASE_MODEL_FIELDS)
    list_filter = ('created',)
    search_fields = ('week__week_start_date',)
    ordering = ('created',)
    list_per_page = ROWS_PER_PAGE
    exclude = BASE_MODEL_FIELDS

    def save_model(self, request: HttpRequest, obj: WeeklyRate, form: ModelForm, change: bool) -> None:
        setCreatedByUpdatedBy(request, obj, change)
        super().save_model(request, obj, form, change)
