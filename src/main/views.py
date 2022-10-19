from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Q
from datetime import timedelta

from distributor.models import Distributor
from human_resources.models import Employee, Task
from . import constant
from .decorators import isAuthenticatedUser
from .forms import CreateUserForm
from .utils import getEmployeesTasks as EmployeeTasks
from .utils import getUserBaseTemplate as base
from .utils import getUserRole


@isAuthenticatedUser
def index(request):
    if request.method == "POST":
        UserName: str = request.POST.get('user_name')
        Password: str = request.POST.get('password')
        User = authenticate(request, username=UserName, password=Password)

        if User is not None:
            login(request, User)
            return redirect(constant.PAGES.INDEX)
        else:
            messages.info(request, "Username or Password is incorrect")

    return render(request, constant.TEMPLATES.INDEX_TEMPLATE)


def about(request):
    context: dict = {}
    return render(request, constant.TEMPLATES.ABOUT_TEMPLATE, context)


def unauthorized(request):
    context: dict = {}
    return render(request, constant.TEMPLATES.UNAUTHORIZED_TEMPLATE)


@login_required(login_url=constant.PAGES.INDEX)
def dashboard(request):
    group = None
    if request.user.groups.exists():
        group = getUserRole(request)

    context: dict = {'group': group}
    return render(request, constant.TEMPLATES.DASHBOARD_TEMPLATE, context)


def logoutUser(request):
    logout(request)
    return redirect(constant.PAGES.INDEX)


def createUserPage(request):
    form = CreateUserForm()
    if request.method == constant.POST:
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

            old_user = request.user
            new_user = User.objects.all().order_by('-id')[0]
            if getUserRole(old_user) == constant.ROLES.DISTRIBUTOR:
                user = Distributor.objects.get(account=old_user)
                Group.objects.get(
                    name=constant.ROLES.DISTRIBUTOR).user_set.add(new_user)
            else:
                user = Employee.objects.get(account=old_user)
                Group.objects.get(name=user.position).user_set.add(new_user)
                if user.position == constant.ROLES.CEO:
                    new_user.is_superuser = True
                    new_user.is_staff = True
                    new_user.is_admin = True
                    new_user.save()

            user.account = new_user
            user.save()

            logout(request)
            old_user.delete()

            messages.info(request, "Please sing in with your new account")

            return redirect(constant.PAGES.INDEX)

    context: dict = {'form': form}
    return render(request, constant.TEMPLATES.CREATE_USER_TEMPLATE, context)


def tasks(request):
    Tasks = Task.objects.filter(~Q(status="Late-Submission") & ~Q(
        status="On-Time"), employee__account=request.user)

    if request.method == constant.POST:
        from django.utils import timezone
        from datetime import datetime

        task_id = request.POST.get('task_id', False)
        task = Task.objects.get(id=int(task_id))
        onTime = request.POST.get(f'onTime{id}', False)
        now = datetime.strftime(timezone.now(), '%Y-%m-%d %H:%M:%s')

        if task.name == "Evaluate employees":
            return redirect(constant.PAGES.WEEKLY_EVALUATION_PAGE)
        elif task.name == "Rate task":
            return redirect(constant.PAGES.TASK_EVALUATION_PAGE)
        elif not task.deadline_date or str(task.deadline_date) >= now:
            task.status = "On-Time"
        else:
            task.status = "Late-Submission"

        task.submission_date = timezone.now()
        task.save()

        if getUserRole(request) != constant.ROLES.HUMAN_RESOURCES:
            emp = Employee.objects.get(position=constant.ROLES.HUMAN_RESOURCES)
            Task.objects.create(
                employee=emp,
                name="Rate task",
                description=f"Don't forget to rate {task.employee.person.name}'s submitted task. '{task.name}' Task.",
                deadline_date=timezone.now() + timedelta(days=3)
            )

    context = {'Tasks': Tasks, 'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    return render(request, constant.TEMPLATES.TASKS_TEMPLATE, context)
