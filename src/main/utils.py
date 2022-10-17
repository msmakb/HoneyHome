from typing import Union
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from human_resources.models import Employee, Task
from . import constant


class Pagination:

    def __init__(self, queryset: QuerySet, page_num: int, paginate_by: int = constant.PAGINATE_BY) -> None:
        self.page_num = page_num
        self.paginator = Paginator(queryset, paginate_by)

    def getPageObject(self) -> QuerySet:
        return self.paginator.get_page(self.page_num)

    @property
    def isPaginated(self) -> bool:
        return True if self.paginator.num_pages > 1 else False


def getRequesterRole(request) -> str:
    return request.user.groups.all()[0].name


def getUserBaseTemplate(request) -> str:
    Role: str = getRequesterRole(request)
    base: str = ''
    for i in Role.split(' '):
        base += i.lower()
        if Role.split(' ')[-1] != i:
            base += '_'
    base += '/base.html'
    return base


def getEmployeesTasks(request) -> QuerySet:
    employee = Employee.objects.get(account=request.user)
    Tasks = Task.objects.filter(~Q(status="Late-Submission") &
                                ~Q(status="On-Time"), employee=employee)

    return Tasks


# def getLastInsertedObjectId(obj: Union[QuerySet, object]) -> int:
#     from django.db import models

#     if not issubclass(type(obj), models.Model) or isinstance(obj, QuerySet):
#         raise "obj must be a QuerySet or a django model."
#     obj_id: int= -1
#     if isinstance(obj, QuerySet):
#         obj = obj.objects.all()

#     try:
#         obj.order_by('-id')[0].id
#     except IndexError: pass
#     return obj_id
