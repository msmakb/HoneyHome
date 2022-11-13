from django import template
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.template.context import RenderContext
from django.urls import reverse

from human_resources.models import Employee, Task

from .. import constants
from ..utils import getUserRole as _getUserRole
from ..utils import resolvePageUrl as _resolvePageUrl

# Register template library
register = template.Library()


@register.simple_tag
def getEmployeeTasks(request: HttpRequest) -> QuerySet:
    employee: Employee = Employee.get(account=request.user)
    Tasks: Task = Task.filter(~Q(status=constants.TASK_STATUS.LATE_SUBMISSION) &
                              ~Q(status=constants.TASK_STATUS.ON_TIME),
                              employee=employee)

    return Tasks


@register.simple_tag
def getUserRole(request: HttpRequest) -> str:
    return _getUserRole(request)


@register.simple_tag(takes_context=True)
def isVarExists(context: RenderContext, name: str) -> bool:
    dicts: dict = context.dicts
    if dicts:
        for d in dicts:
            if name in d:
                return True
    return False


@register.simple_tag
def getNamespace(request: HttpRequest) -> str:
    return f"{_getUserRole(request).replace(' ', '')}:"
