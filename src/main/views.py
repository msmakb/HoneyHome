from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Q
from datetime import timedelta

from distributor.models import Distributor
from human_resources.models import Employee, Task
from .decorators import isAuthenticatedUser
from .forms import CreateUserForm
from .utils import getEmployeesTasks as EmployeeTasks
from .utils import getUserBaseTemplate as base


@isAuthenticatedUser
def index(request):
    if request.method == "POST":
        UserName = request.POST.get('user_name')
        Password = request.POST.get('password')
        User = authenticate(request, username=UserName, password=Password)

        if User is not None:
            login(request, User)
            return redirect('Index')
        else:
            messages.info(request, "Username or Password is incorrect")

    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def unauthorized(request):
    return render(request, 'unauthorized.html')


@login_required(login_url='Index')
def dashboard(request):
    group = None
    if request.user.groups.exists():
        group = request.user.groups.all()[0].name
    return render(request, 'Dashboard.html', {'group': group})


def logoutUser(request):
    logout(request)
    return redirect('Index')


def createUserPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

            old_user = request.user
            new_user = User.objects.all().order_by('-id')[0]
            if old_user.groups.all()[0].name == "Distributor":
                user = Distributor.objects.get(account=old_user)
                Group.objects.get(name="Distributor").user_set.add(new_user)
            else:
                user = Employee.objects.get(account=old_user)
                Group.objects.get(name=user.position).user_set.add(new_user)
                if user.position == "CEO":
                    new_user.is_superuser = True
                    new_user.is_staff = True
                    new_user.is_admin = True
                    new_user.save()

            user.account = new_user
            user.save()

            logout(request)
            old_user.delete()

            messages.info(request, "Please sing in with your new account")

            return redirect('Index')

    template = 'create_user.html'
    context = {'form': form}
    return render(request, template, context)


def tasks(request):
    Tasks = Task.objects.filter(~Q(status="Late-Submission") & ~Q(
        status="On-Time"), employee__account=request.user)

    if request.method == "POST":
        from django.utils import timezone
        from datetime import datetime

        task_id = request.POST.get('task_id', False)
        task = Task.objects.get(id=int(task_id))
        onTime = request.POST.get(f'onTime{id}', False)
        now = datetime.strftime(timezone.now(), '%Y-%m-%d %H:%M:%s')

        if task.name == "Evaluate employees":
            return redirect("WeeklyEvaluationPage")
        elif task.name == "Rate task":
            return redirect("TaskEvaluationPage")
        elif not task.deadline_date or str(task.deadline_date) >= now:
            task.status = "On-Time"
        else:
            task.status = "Late-Submission"

        task.submission_date = timezone.now()
        task.save()

        if request.user.groups.all()[0].name != "Human Resources":
            emp = Employee.objects.get(position='Human Resources')
            Task.objects.create(
                employee=emp,
                name="Rate task",
                description=f"Don't forget to rate {task.employee.person.name}'s submitted task. '{task.name}' Task.",
                deadline_date=timezone.now() + timedelta(days=3)
            )

    context = {'Tasks': Tasks, 'base': base(
        request), 'EmployeeTasks': EmployeeTasks(request)}
    return render(request, 'tasks.html', context)
