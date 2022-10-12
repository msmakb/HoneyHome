from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from human_resources.models import Employee, Task


class Pagination:

    def __init__(self, queryset, page_num, paginate_by=10) -> None:
        self.page_num = page_num
        self.paginator = Paginator(queryset, paginate_by)

    def getPageObject(self) -> QuerySet:
        return self.paginator.get_page(self.page_num)

    @property
    def isPaginated(self) -> bool:
        return True if self.paginator.num_pages > 1 else False


def getUserBaseTemplate(request) -> str:
    group = request.user.groups.all()[0].name
    base = ""
    for i in str(group).split(' '):
        base += i.lower()
        if str(group).split(' ')[-1] != i:
            base += '_'
    base += '/base.html'
    return base


def getEmployeesTasks(request) -> QuerySet:
    employee = Employee.objects.get(account=request.user)
    Tasks = Task.objects.filter(~Q(status="Late-Submission") &
                                ~Q(status="On-Time"), employee=employee)

    return Tasks
