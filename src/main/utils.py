from typing import Union
from urllib import request
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from human_resources.models import Employee, Task
from .constant import PAGINATE_BY


class Pagination:

    def __init__(self, queryset: QuerySet, page_num: int, paginate_by: int = PAGINATE_BY) -> None:
        self.page_num = page_num
        self.paginator = Paginator(queryset, paginate_by)

    def getPageObject(self) -> QuerySet:
        return self.paginator.get_page(self.page_num)

    @property
    def isPaginated(self) -> bool:
        return True if self.paginator.num_pages > 1 else False


def getUserRole(user) -> str:
    from django.contrib.auth.models import User

    requester = None
    if isinstance(user, User):
        requester = user
    else:
        requester = user.user
    return requester.groups.all()[0].name


def getUserBaseTemplate(request) -> str:
    Role: str = getUserRole(request)
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
