import logging
from logging import Logger
from typing import Any

from django.db.models import Q
from django.db.models.functions import Lower
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from distributor.models import Distributor
from main import constants
from main import messages as MSG
from main.models import Person
from main.utils import Pagination
from main.utils import getUserBaseTemplate as base
from main.utils import resolvePageUrl

from .evaluation import (allEmployeesMonthlyEvaluations,
                         allEmployeesMonthlyOverallEvaluation,
                         allEmployeesMonthlyTaskRate,
                         allEmployeesWeeklyEvaluations, getEvaluation,
                         getTaskRateFrom)
from .forms import AddPersonForm, AddTaskForm, EmployeeForm
from .models import Employee, Task, TaskRate, Week, WeeklyRate
from .utils import isRequesterCEO, isUserAllowedToModify

logger: Logger = logging.getLogger(constants.LOGGERS.HUMAN_RESOURCES)


# ------------------------------Dashboard------------------------------ #
def humanResourcesDashboard(request: HttpRequest) -> HttpResponse:
    in_progress: int = Task.countFiltered(
        status=constants.TASK_STATUS.IN_PROGRESS)
    unsubmitted: int = Task.countFiltered(
        Q(status=constants.TASK_STATUS.IN_PROGRESS) |
        Q(status=constants.TASK_STATUS.OVERDUE))
    employees: int = Employee.countAll()
    distributors: int = Distributor.countAll()

    context: dict[str, Any] = {
        'in_progress': in_progress,
        'unsubmitted': unsubmitted,
        'employees': employees,
        'distributors': distributors,
        'employees_weekly_rate': allEmployeesWeeklyEvaluations(),
        'employees_monthly_rate': allEmployeesMonthlyEvaluations(),
        'allEmployeesMonthlyTaskRate': allEmployeesMonthlyTaskRate(),
        'employees_monthly_rate_overall_performance': allEmployeesMonthlyOverallEvaluation(),
    }
    return render(request, constants.TEMPLATES.HUMAN_RESOURCES_DASHBOARD_TEMPLATE, context)


# ------------------------------Employees------------------------------ #
def employeesPage(request: HttpRequest) -> HttpResponse:
    employees: QuerySet[Employee] = Employee.getAllOrdered(
        Lower('person__name'))
    page: str = request.GET.get('page')
    pagination = Pagination(employees, int(page) if page is not None else 1)
    page_obj: QuerySet[Task] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {'page_obj': page_obj, 'is_paginated': is_paginated,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.EMPLOYEES_TEMPLATE, context)


def addEmployeePage(request: HttpRequest) -> HttpResponse:
    person_form = AddPersonForm(request)
    employee_form = EmployeeForm(request)
    if request.method == constants.POST_METHOD:
        person_form = AddPersonForm(request, request.POST)
        employee_form = EmployeeForm(request, request.POST)
        if person_form.is_valid() and employee_form.is_valid():
            person_form.save()
            # Signal sent after the creations of the employee
            employee_form.save()
            MSG.EMPLOYEE_ADDED(request)

            return redirect(resolvePageUrl(request, constants.PAGES.EMPLOYEES_PAGE))

    context: dict[str, Any] = {'PersonForm': person_form, 'employee_form': employee_form,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.ADD_EMPLOYEE_TEMPLATE, context)


def employeePage(request: HttpRequest, pk: int, hash=None) -> HttpResponse:
    employee: Employee = get_object_or_404(Employee, id=pk)
    evaluation: dict[str, float | Employee] = getEvaluation(emp_id=pk)
    if not isUserAllowedToModify(request.user, employee.position, constants.ROLES.CEO):
        return redirect(constants.PAGES.UNAUTHORIZED_PAGE)
    if request.method == constants.POST_METHOD:
        employee.person.setPhoto(request, request.FILES["image_file"])
        MSG.EMPLOYEE_PHOTO_UPDATED(request)

    context: dict[str, Any] = {'Employee': employee, 'Evaluation': evaluation,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.EMPLOYEE_RECORD_TEMPLATE, context)


def updateEmployeePage(request: HttpRequest, pk: int) -> HttpResponse:
    employee: Employee = get_object_or_404(Employee, id=pk)
    person: Person = Person.get(id=employee.person.id)
    if not isUserAllowedToModify(request.user, employee.position, constants.ROLES.CEO):
        return redirect(constants.PAGES.UNAUTHORIZED_PAGE)
    employee_form = EmployeeForm(request, instance=employee)
    person_form = AddPersonForm(request, instance=person)
    if request.method == constants.POST_METHOD:
        person_form = AddPersonForm(request, request.POST, instance=person)
        employee_form = EmployeeForm(request, request.POST, instance=employee)
        if person_form.is_valid() and employee_form.is_valid():
            person_form.save()
            employee_form.save()
            MSG.EMPLOYEE_DATA_UPDATED(request)

            return redirect(resolvePageUrl(request, constants.PAGES.EMPLOYEE_RECORD_PAGE), pk)

    context: dict[str, Any] = {'PersonForm': person_form, 'employee_form': employee_form,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.UPDATE_EMPLOYEE_TEMPLATE, context)


def deleteEmployeePage(request: HttpRequest, pk: int) -> HttpResponse:
    employee: Employee = get_object_or_404(Employee, id=pk)
    if not isUserAllowedToModify(request.user, employee.position, constants.ROLES.CEO):
        return redirect(constants.PAGES.UNAUTHORIZED_PAGE)
    if request.method == constants.DELETE_METHOD:
        employee.delete(request)
        MSG.EMPLOYEE_REMOVED(request)

        return redirect(resolvePageUrl(request, constants.PAGES.EMPLOYEES_PAGE))

    context: dict[str, Any] = {'Employee': employee, 'base': base(request)}
    return render(request, constants.TEMPLATES.DELETE_EMPLOYEE_TEMPLATE, context)


# ------------------------------Distributors------------------------------ #
def distributorsPage(request: HttpRequest) -> HttpResponse:
    distributors: QuerySet[Distributor] = Distributor.getAllOrdered(
        Lower('person__name'))
    page: str = request.GET.get('page')
    pagination = Pagination(distributors, int(page) if page is not None else 1)
    page_obj: QuerySet[Task] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {'page_obj': page_obj, 'is_paginated': is_paginated,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.DISTRIBUTORS_TEMPLATE, context)


def addDistributorPage(request: HttpRequest) -> HttpResponse:
    person_form = AddPersonForm(request, )
    if request.method == constants.POST_METHOD:
        person_form = AddPersonForm(request, request.POST)
        if person_form.is_valid():
            person_form.save()
            # Signal sent after the creations of the distributor
            Distributor.create(request)
            MSG.DISTRIBUTOR_ADDED(request)

            return redirect(resolvePageUrl(request, constants.PAGES.DISTRIBUTORS_PAGE))

    context: dict[str, Any] = {
        'PersonForm': person_form, 'base': base(request)}
    return render(request, constants.TEMPLATES.ADD_DISTRIBUTOR_TEMPLATE, context)


def distributorPage(request: HttpRequest, pk: int) -> HttpResponse:
    distributor: Distributor = get_object_or_404(Distributor, id=pk)
    if request.method == constants.POST_METHOD:
        distributor.person.setPhoto(request, request.FILES["image_file"])
        MSG.DISTRIBUTOR_PHOTO_UPDATED(request)

    context: dict[str, Any] = {'Distributor': distributor,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.DISTRIBUTOR_RECORD_TEMPLATE, context)


def updateDistributorPage(request: HttpRequest, pk: int) -> HttpResponse:
    distributor: Distributor = get_object_or_404(Distributor, id=pk)
    person: Person = Person.get(id=distributor.person.id)
    person_form = AddPersonForm(request, instance=person)
    if request.method == constants.POST_METHOD:
        person_form = AddPersonForm(request, request.POST, instance=person)
        if person_form.is_valid():
            person_form.save()
            MSG.DISTRIBUTOR_DATA_UPDATED(request)

            return redirect(resolvePageUrl(request, constants.PAGES.DISTRIBUTOR_RECORD_PAGE), pk)

    context: dict[str, Any] = {'PersonForm': person_form, 'distributor_id': distributor.id,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.UPDATE_DISTRIBUTOR_TEMPLATE, context)


def deleteDistributorPage(request: HttpRequest, pk: int) -> HttpResponse:
    distributor: Distributor = get_object_or_404(Distributor, id=pk)
    if request.method == constants.DELETE_METHOD:
        distributor.delete(request)
        MSG.DISTRIBUTOR_REMOVED(request)

        return redirect(resolvePageUrl(request, constants.PAGES.DISTRIBUTORS_PAGE))

    context: dict[str, Any] = {'Distributor': distributor,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.DELETE_DISTRIBUTOR_TEMPLATE, context)


# ------------------------------Tasks------------------------------ #
def employeeTasksPage(request: HttpRequest) -> HttpResponse:
    tasks: QuerySet[Task] = Task.getAllOrdered('updated', reverse=True)
    page: str = request.GET.get('page')
    pagination = Pagination(tasks, int(page) if page is not None else 1)
    page_obj: QuerySet[Task] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {'page_obj': page_obj, 'is_paginated': is_paginated,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.EMPLOYEES_TASKS_TEMPLATE, context)


def addTaskPage(request: HttpRequest) -> HttpResponse:
    form = AddTaskForm(request)
    if request.method == constants.POST_METHOD:
        form = AddTaskForm(request, request.POST)
        if form.is_valid():
            form.save()
            MSG.TASK_ADDED(request)

            return redirect(resolvePageUrl(request, constants.PAGES.EMPLOYEES_TASKS_PAGE))

    context: dict[str, Any] = {'form': form, 'base': base(request)}
    return render(request, constants.TEMPLATES.ADD_TASK_TEMPLATE, context)


def taskPage(request: HttpRequest, pk: int) -> HttpResponse:
    task: Task = get_object_or_404(Task, id=pk)
    if not isUserAllowedToModify(request.user, task.employee.position,
                                 constants.ROLES.HUMAN_RESOURCES):
        return redirect(constants.PAGES.UNAUTHORIZED_PAGE)
    try:
        task_rate: TaskRate = TaskRate.get(task=task)
    except TaskRate.DoesNotExist:
        task_rate = None

    context: dict[str, Any] = {'Task': task, 'TaskRate': task_rate,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.DETAILED_TASK_TEMPLATE, context)


def updateTaskPage(request: HttpRequest, pk: int) -> HttpResponse:
    task: Task = get_object_or_404(Task, id=pk)
    if not isUserAllowedToModify(request.user, task.employee.position,
                                 constants.ROLES.HUMAN_RESOURCES):
        return redirect(constants.PAGES.UNAUTHORIZED_PAGE)

    form = AddTaskForm(request, instance=task)
    if request.method == constants.POST_METHOD:
        form = AddTaskForm(request, request.POST, instance=task)
        if form.is_valid():
            form.save()
            MSG.TASK_DATA_UPDATED(request)

            return redirect(resolvePageUrl(request, constants.PAGES.DETAILED_TASK_PAGE), pk)

    context: dict[str, Any] = {'form': form, 'base': base(request)}
    return render(request, constants.TEMPLATES.UPDATE_TASK_TEMPLATE, context)


def deleteTaskPage(request: HttpRequest, pk: int) -> HttpResponse:
    task: Task = get_object_or_404(Task, id=pk)
    if not isUserAllowedToModify(request.user, task.employee.position,
                                 constants.ROLES.HUMAN_RESOURCES):
        return redirect(constants.PAGES.UNAUTHORIZED_PAGE)

    if request.method == constants.DELETE_METHOD:
        task.delete(request)
        MSG.TASK_REMOVED(request)

        return redirect(resolvePageUrl(request, constants.PAGES.EMPLOYEES_TASKS_PAGE))

    context: dict[str, Any] = {'Task': task, 'base': base(request)}
    return render(request, constants.TEMPLATES.DELETE_TASK_TEMPLATE, context)


# ------------------------------Evaluation------------------------------ #
def evaluationPage(request: HttpRequest) -> HttpResponse:
    context: dict[str, Any] = {'evaluation': getEvaluation(),
                               'base': base(request)}
    return render(request, constants.TEMPLATES.EVALUATION_TEMPLATE, context)


# Needs fix
def weeklyEvaluationPage(request: HttpRequest) -> HttpResponse:
    weeks: QuerySet[Week] = Week.filter(is_rated=False)

    context: dict[str, Any] = {'week_to_rate_exists': True,
                               'base': base(request)}
    if not weeks.exists():
        MSG.EVALUATION_DONE(request)
        context['week_to_rate_exists'] = False
    else:
        Employees: QuerySet[Employee] = Employee.filter(~Q(position=constants.ROLES.CEO) &
                                                        ~Q(position=constants.ROLES.HUMAN_RESOURCES))
        context['Employees'] = Employees
        if len(weeks) > 1:
            unrated_weeks_to_delete: int = 0
            for index, week in enumerate(weeks):
                if index == len(weeks) - 1:
                    MSG.MANY_WEEKS(request)
                    MSG.WEEKS_DELETED(request, unrated_weeks_to_delete)
                    MSG.INFORM_CEO(request)
                else:
                    week.delete(constants.SYSTEM_NAME)
                    unrated_weeks_to_delete += 1
        if request.method == constants.POST_METHOD:
            for emp in Employees:
                val: float = request.POST.get(f'val{str(emp.id)}', False)
                WeeklyRate.create(
                    request,
                    week=weeks[0],
                    employee=emp,
                    rate=int(val))

            # Automatically rate the HR depends on his last week task rate
            hr: Employee = Employee.get(
                position=constants.ROLES.HUMAN_RESOURCES)
            WeeklyRate.create(
                constants.SYSTEM_NAME,
                week=weeks[0],
                employee=hr,
                rate=getTaskRateFrom(hr.id, 7))

            weeks[0].setRated(request, True)

            task: Task = None
            something_wrong: bool = False
            try:
                task = Task.get(name="Evaluate employees",
                                employee=hr,
                                is_rated=False)
            except Task.MultipleObjectsReturned:
                tasks: QuerySet[Task] = Task.filter(name="Evaluate employees",
                                                    employee=hr,
                                                    is_rated=False)
                for index, _task in enumerate(tasks):
                    if index == len(tasks) - 1:
                        task = _task
                    else:
                        _task.delete(constants.SYSTEM_NAME)
            except Task.DoesNotExist:
                MSG.SOMETHING_WRONG(request)
                something_wrong = True

            if not something_wrong:
                task.setStatus(constants.SYSTEM_NAME,
                               constants.TASK_STATUS.ON_TIME)
                task.setSubmissionDate(constants.SYSTEM_NAME,
                                       timezone.now())
                task.setRated(constants.SYSTEM_NAME, True)
                TaskRate.create(constants.SYSTEM_NAME, task=task,
                                on_time_rate=5, rate=5)

            return redirect(resolvePageUrl(request, constants.PAGES.EVALUATION_PAGE))

    return render(request, constants.TEMPLATES.WEEKLY_EVALUATION_TEMPLATE, context)


# Needs fix
def taskEvaluationPage(request: HttpRequest) -> HttpResponse:
    if isRequesterCEO:
        Tasks: QuerySet[Task] = Task.orderFiltered(
            Lower('employee__person__name'),
            ~Q(status=constants.TASK_STATUS.IN_PROGRESS)
            & ~Q(status=constants.TASK_STATUS.OVERDUE),
            is_rated=False
        )
    else:
        Tasks: QuerySet[Task] = Task.orderFiltered(
            Lower('employee__person__name'),
            ~Q(status=constants.TASK_STATUS.IN_PROGRESS)
            & ~Q(status=constants.TASK_STATUS.OVERDUE),
            ~Q(employee__position=constants.ROLES.HUMAN_RESOURCES),
            is_rated=False
        )
    if request.method == constants.POST_METHOD:
        id: str = request.POST.get('id', False)
        val: str = request.POST.get(f'val{id}', False)
        task: Task = Task.get(id=int(id))
        on_time: float = 5.0
        if task.status != constants.TASK_STATUS.ON_TIME:
            on_time = 2.5
        TaskRate.create(
            request,
            task=task,
            on_time_rate=on_time,
            rate=float(val))
        task.setRated(request, True)

        auto_task: Task = Task.get(
            employee__position=constants.ROLES.HUMAN_RESOURCES,
            description=f"Don't forget to rate {task.employee.person.name}'s "
            + "submitted task. '{task.name}' Task.",
            is_rated=False)

        if not isRequesterCEO:
            on_time: float = 5.0
            status = constants.TASK_STATUS.ON_TIME
            if auto_task.status != constants.TASK_STATUS.IN_PROGRESS:
                on_time = 2.5
                status = constants.TASK_STATUS.LATE_SUBMISSION

            TaskRate.create(task=auto_task,
                            on_time_rate=on_time,
                            rate=float(5))
            auto_task.setStatus(constants.SYSTEM_NAME, status)
            auto_task.setRated(constants.SYSTEM_NAME, True)
            auto_task.setSubmissionDate(constants.SYSTEM_NAME, timezone.now())
        else:
            auto_task.delete(constants.SYSTEM_NAME)

        MSG.TASKS_EVALUATION_DONE(request)

    if not Tasks.exists():
        MSG.RATE_TASKS_DONE(request)

    context: dict[str, Any] = {'Tasks': Tasks, 'base': base(request)}
    return render(request, constants.TEMPLATES.TASK_EVALUATION_TEMPLATE, context)
