import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from distributor.models import Distributor
from human_resources.models import Employee, Task

from . import constants
from . import messages as MSG
from .decorators import isAuthenticatedUser
from .forms import CreateUserForm
from .utils import getUserBaseTemplate as base
from .utils import getUserRole

logger = logging.getLogger(constants.LOGGERS.MAIN)


@isAuthenticatedUser
def index(request: HttpRequest) -> HttpResponse:
    if request.method == constants.POST:
        print(request.POST)
        UserName: str = request.POST.get('user_name')
        Password: str = request.POST.get('password')
        user: User = authenticate(
            request, username=UserName, password=Password)
        print(user.get_full_name())

        if user is not None:
            login(request, user)
            return redirect(constants.PAGES.INDEX)
        else:
            MSG.INCORRECT_INFO(request)

    return render(request, constants.TEMPLATES.INDEX_TEMPLATE)


def about(request: HttpRequest) -> HttpResponse:
    return render(request, constants.TEMPLATES.ABOUT_TEMPLATE)


def unauthorized(request: HttpRequest) -> HttpResponse:
    logger.warning(
        f"The user [{request.user}] is unauthorized to view this page")
    return render(request, constants.TEMPLATES.UNAUTHORIZED_TEMPLATE)


# this is admin dashboard 'for testing purpose only'
def dashboard(request: HttpRequest) -> HttpResponse:
    group: str = getUserRole(request)
    context: dict = {'group': group}
    return render(request, constants.TEMPLATES.DASHBOARD_TEMPLATE, context)


def logoutUser(request: HttpRequest) -> HttpResponse:
    try:
        logout(request)
    except AttributeError:
        pass
    return redirect(constants.PAGES.INDEX)


def createUserPage(request: HttpRequest) -> HttpResponse:
    form = CreateUserForm()
    if request.method == constants.POST:
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

            old_user: User = request.user
            # Get last inserted user object
            new_user: User = User.objects.all().order_by('-id')[0]
            new_user.first_name = old_user.first_name
            new_user.last_name = old_user.last_name
            if getUserRole(old_user) == constants.ROLES.DISTRIBUTOR:
                user: Distributor = Distributor.get(account=old_user)
                Group.objects.get(name=constants.ROLES.DISTRIBUTOR
                                  ).user_set.add(new_user)
            else:
                user: Employee = Employee.get(account=old_user)
                Group.objects.get(name=user.position).user_set.add(new_user)
                if user.position == constants.ROLES.CEO:
                    new_user.is_superuser = True
                    new_user.is_staff = True
                    new_user.save()

            user.setAccount(request, new_user)
            logout(request)
            old_user.delete()
            MSG.LOGIN_WITH_NEW_ACCOUNT(request)

            return redirect(constants.PAGES.INDEX)

    context: dict = {'form': form}
    return render(request, constants.TEMPLATES.CREATE_USER_TEMPLATE, context)


# Needs fix
def tasks(request: HttpRequest) -> HttpResponse:
    Tasks: Task = Task.filter(~Q(status=constants.TASK_STATUS.LATE_SUBMISSION) & ~Q(
        status=constants.TASK_STATUS.ON_TIME), employee__account=request.user)

    if request.method == constants.POST:

        task_id = request.POST.get('task_id', False)
        task: Task = Task.get(id=int(task_id))
        # onTime = request.POST.get(f'onTime{id}', False)
        now: timezone.datetime = timezone.now()

        if task.task == "Evaluate employees":
            return redirect(constants.PAGES.WEEKLY_EVALUATION_PAGE)
        elif task.task == "Rate task":
            return redirect(constants.PAGES.TASK_EVALUATION_PAGE)
        elif not task.deadline_date or task.deadline_date >= now:
            task.status = constants.TASK_STATUS.ON_TIME
        else:
            task.status = constants.TASK_STATUS.LATE_SUBMISSION

        task.submission_date = timezone.now()
        task.save()

        if getUserRole(request) != constants.ROLES.HUMAN_RESOURCES:
            emp = Employee.get(position=constants.ROLES.HUMAN_RESOURCES)
            Task.create("Auto Task System",
                        employee=emp,
                        task="Rate task",
                        description=f"Don't forget to rate {task.employee.person.name}'s submitted task. '{task.task}' Task.",
                        deadline_date=timezone.now() + timezone.timedelta(days=3)
                        )

    context = {'Tasks': Tasks, 'base': base(request)}
    return render(request, constants.TEMPLATES.TASKS_TEMPLATE, context)
