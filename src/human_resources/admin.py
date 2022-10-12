from django.contrib import admin
from .models import Employee, Task, TaskRate, Week, WeeklyRate


# Employee model
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'person', 'account', 'position')


# Task model
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'name', 'description',
                    'status', 'receiving_date', 'deadline_date',
                    'submission_date', 'is_rated')


# Task rate model
class TaskRateAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'on_time_rate', 'rate')


# Week model
class WeekAdmin(admin.ModelAdmin):
    list_display = ('id', 'week_start_date', 'week_end_date', 'is_rated')


# Weekly rate model
class WeeklyRateAdmin(admin.ModelAdmin):
    list_display = ('id', 'week', 'employee', 'rate')


# Registering models in admen page
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskRate, TaskRateAdmin)
admin.site.register(Week, WeekAdmin)
admin.site.register(WeeklyRate, WeeklyRateAdmin)
