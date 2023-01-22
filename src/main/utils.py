import csv
import logging
from logging import Logger
from typing import Any, Callable, Optional, Union

from django.contrib.auth.models import User
from django.core.exceptions import EmptyResultSet
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.forms import ModelForm
from django.utils.timezone import datetime

from human_resources.models import Employee, Task

from . import constants
from .models import BaseModel

logger: Logger = logging.getLogger(constants.LOGGERS.MAIN)
logger_models: Logger = logging.getLogger(constants.LOGGERS.MODELS)


class Pagination:

    def __init__(self, queryset: QuerySet, page_num: int, paginate_by: int = constants.ROWS_PER_PAGE) -> None:
        self.page_num: int = page_num
        self.paginator: Paginator = Paginator(queryset, paginate_by)

    def getPageObject(self) -> QuerySet | dict[str, Any]:
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
    if self.is_valid():
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
                raise TypeError("'NoneTypeError' Something went wrong!!")
            created_by: str = instance.created_by
        return created_by
    else:
        return None


def clean_form_updated_by(self: ModelForm) -> str:
    if self.is_valid():
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
    else:
        return None


def exportAsCsv(
    queryset: QuerySet,
    fileName: Optional[str] = str(datetime.today()),
    fields: Optional[list[str] | str] = '__all__',
    labels_to_change: Optional[dict[str, str] | None] = None,
    values_to_change: Optional[dict[str, Callable] | None] = None,
    default_empty_value: Optional[str] = "-"
) -> HttpResponse:
    """
    Exports a given queryset to a CSV file, which can be downloaded by the user.

    :param queryset: The queryset to be exported. Must be a valid Django queryset.
    :type queryset: QuerySet
    :param fileName: The desired file name for the exported CSV file, without the file extension.
    :type fileName: str, optional
    :param fields: A list of fields that should be included in the exported CSV file. Can also be '__all__' to export all fields.
    :type fields: list[str] | str, optional
    :param labels_to_change: A dictionary where the keys are the original field names in the queryset and the values are the new labels to be used in the exported CSV file.
    :type labels_to_change: dict[str, str] | None, optional
    :param values_to_change: A dictionary where the keys are the original field names in the queryset and the values are callable functions to be applied to the field values before exporting. The callable function accepts one parameter which is the field need to be modified.
    :type values_to_change: dict[str, Callable] | None, optional
    :param default_empty_value: The value to be used for fields that are empty or None.
    :type default_empty_value: str, optional
    :raises EmptyResultSet: If the provided queryset is empty, a EmptyResultSet exception will be raised with the message "The queryset provided is empty."
    :return: A response object that can be used to download the exported CSV file.
    :rtype: HttpResponse

    """

    if not queryset.exists():
        raise EmptyResultSet("The queryset provided is empty.")

    if isinstance(fields, str):
        if fields == '__all__':
            fields = [field.name for field in queryset.first()._meta.get_fields()]
        else:
            fields = fields.split(' ')

    queryset: QuerySet[BaseModel] = queryset.values(*fields)
    response: HttpResponse = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{fileName}.csv"'
    writer = csv.writer(response)

    titles: list = []
    if labels_to_change:
        for row in fields:
            titles.append(labels_to_change[row]
                          if row in labels_to_change else row)
    else:
        titles = fields

    writer.writerow([title.title() for title in titles])

    for model_row in queryset:
        row: list[str] = []
        for key, value in model_row.items():
            if values_to_change and key in values_to_change:
                row.append(str(values_to_change[key](
                    value)) if value else default_empty_value)
            else:
                row.append(str(value) if value else default_empty_value)
        writer.writerow(row)

    return response


def getUserRole(requester: Union[HttpRequest, User]) -> str | None:
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
    return 'base.html'


def getEmployeesTasks(request: HttpRequest) -> QuerySet[Task]:
    employee: Employee = Employee.get(account=request.user)
    Tasks: QuerySet[Task] = Task.filter(~Q(status=constants.TASK_STATUS.LATE_SUBMISSION) &
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
