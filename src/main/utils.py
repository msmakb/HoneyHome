import logging
from typing import Union

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest

from human_resources.models import Employee, Task

from . import constants
from .models import BaseModel

logger = logging.getLogger(constants.LOGGERS.MAIN)
logger_models = logging.getLogger(constants.LOGGERS.MODELS)


class Pagination:

    def __init__(self, queryset: QuerySet, page_num: int, paginate_by: int = constants.ROWS_PER_PAGE):
        self.page_num: int = page_num
        self.paginator: Paginator = Paginator(queryset, paginate_by)

    def getPageObject(self) -> QuerySet:
        return self.paginator.get_page(self.page_num)

    @property
    def isPaginated(self) -> bool:
        return True if self.paginator.num_pages > 1 else False


def setCreatedByUpdatedBy(requester: Union[HttpRequest, str], obj: BaseModel, change=False):
    user: str = ''
    if not isinstance(obj, BaseModel):
        raise TypeError("The object must be a child of BaseModel.")
    if not requester:
        user = 'Unknown User'
    elif isinstance(requester, HttpRequest):
        _user: User = requester.user
        user = _user.get_full_name()
    else:
        try:
            user = str(requester)
        except Exception:
            raise TypeError(
                "'Requester' must be HttpRequest object or string.")
    if change:
        obj.setUpdatedBy(user)
        logger_models.info(f"Database change in {obj.__class__.__name__} at object "
                           + f"ID: {obj.id} By: {user}")
    else:
        obj.setCreatedBy(user)
        obj.setUpdatedBy(user)
        logger_models.info(
            f"Database change in { obj.__class__.__name__} adding new object. "
            + f"ID: {obj.id} By: {user}")


def clean_form_created_by(self: ModelForm, object_str_representation: str) -> str:
    try:
        user: User = self.request.user
    except:
        raise TypeError(
            "Request must be passed in the form and declared as self.request")
    instance: BaseModel = self.instance
    created = not instance.id
    if created:
        created_by: str = user.get_full_name()
        logger.info(f"Database change in [{self.__class__.Meta.model.__name__}] "
                    + f"adding new object. [{object_str_representation}] By: {created_by}")
    else:
        if not instance.created_by:
            raise "Ops.. Something went wrong!!"
        created_by: str = instance.created_by
    return created_by


def clean_form_updated_by(self: ModelForm) -> str:
    try:
        user: User = self.request.user
    except:
        raise TypeError(
            "Request must be passed in the form and declared as self.request")
    instance: BaseModel = self.instance
    updated_by: str = user.get_full_name()
    created = not instance.id
    if not created:
        logger.info(f"Database change in [{self.__class__.Meta.model.__name__}] "
                    + f"at object [{instance.__str__()}] By: {updated_by}")
    return updated_by


def getUserRole(requester: Union[HttpRequest, User]) -> str:
    user: User = None
    if isinstance(requester, User):
        user = requester
    elif isinstance(requester, HttpRequest):
        user = requester.user
    else:
        raise ValueError("Requester must be a User or HttpRequest object.")
    try:
        user_groups = user.groups.all()[0]
        return user_groups.name
    except IndexError:
        return None


def getUserBaseTemplate(request: HttpRequest) -> str:
    Role: str = getUserRole(request)
    base: str = ''
    for i in Role.split(' '):
        base += i.lower()
        if Role.split(' ')[-1] != i:
            base += '_'
    base += '/base.html'
    return base


def getEmployeesTasks(request: HttpRequest) -> QuerySet:
    employee: Employee = Employee.get(account=request.user)
    Tasks: Task = Task.filter(~Q(status=constants.TASK_STATUS.LATE_SUBMISSION) &
                              ~Q(status=constants.TASK_STATUS.ON_TIME),
                              employee=employee)

    return Tasks


def getClientIp(request: HttpRequest) -> str:
    http_x_forwarded_for: str = request.META.get('HTTP_X_FORWARDED_FOR')
    if http_x_forwarded_for:
        ip: str = http_x_forwarded_for.split(',')[0]
    else:
        ip: str = request.META.get('REMOTE_ADDR')
    return ip


def getUserAgent(request: HttpRequest) -> str:
    if request.META.get('HTTP_USER_AGENT'):
        return request.META.get('HTTP_USER_AGENT')
    return request.headers.get('User-Agent', 'Unknown')


def resolvePageUrl(request: HttpRequest, page: str) -> str:
    return f"{getUserRole(request).replace(' ', '')}:{page}"
