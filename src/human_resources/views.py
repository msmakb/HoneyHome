from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from distributor.models import Distributor
from main.decorators import allowedUsers
from main.models import Person
from main.utils import getEmployeesTasks as EmployeeTasks
from main.utils import getUserBaseTemplate as base

from . import alerts
from .evaluation import (getEvaluation, getTaskRateFrom,
                         allEmployeesWeeklyEvaluations,
                         allEmployeesMonthlyEvaluations,
                         allEmployeesMonthlyOverallEvaluation,
                         allEmployeesMonthlyTaskRate)
from .forms import AddPersonForm, EmployeePositionForm, AddTaskForm
from .models import Employee, Task, TaskRate, Week, WeeklyRate
from .utils import isUserAllowedToModify, isRequesterCEO

from django.views.generic.list import ListView

# ------------------------------Dashboard------------------------------ #


@allowedUsers(['Human Resources'])
def humanResourcesDashboard(request):
    # Count in-progress Tasks
    in_progress = Task.objects.filter(status='In-Progress').count()
    # Count unsubmitted Tasks
    unsubmitted = Task.objects.filter(
        Q(status="In-Progress") | Q(status="Overdue")).count()
    # Count employees
    employees = Employee.objects.all().count()
    # Count distributors
    distributors = Distributor.objects.all().count()

    context = {'EmployeeTasks': EmployeeTasks(request),
               'in_progress': in_progress,
               'unsubmitted': unsubmitted,
               'employees': employees,
               'distributors': distributors,
               'employees_weekly_rate': allEmployeesWeeklyEvaluations(),
               'employees_monthly_rate': allEmployeesMonthlyEvaluations(),
               'allEmployeesMonthlyTaskRate': allEmployeesMonthlyTaskRate(),
               'employees_monthly_rate_overall_performance': allEmployeesMonthlyOverallEvaluation(),
               }
    template = 'human_resources/dashboard.html'
    return render(request, template, context)


# ------------------------------Employees------------------------------ #
def EmployeesPage(request):
    # Fetch all employees' data from database
    Employees = Employee.objects.all().order_by(Lower('person__name'))

    context = {'Employees': Employees, 'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/employees.html'
    return render(request, template, context)


def AddEmployeePage(request):
    # Setting up the forms
    person_form = AddPersonForm()
    position_form = EmployeePositionForm()
    # Check if it is a post method
    if request.method == 'POST':
        person_form = AddPersonForm(request.POST)
        position_form = EmployeePositionForm(request.POST)
        # If the forms are valid
        if person_form.is_valid() and position_form.is_valid():
            # Create person
            person_form.save()
            # Add new employee
            position = position_form['position'].value()
            # Create new employee and a signal will be sent to run onAddingNewEmployee function in signals.py file
            Employee.objects.create(position=position)
            alerts.employee_added(request)

            if isRequesterCEO(request):
                return redirect('EmployeesPage-CEO')
            else:
                return redirect('EmployeesPage')

    context = {'PersonForm': person_form, 'position_form': position_form,
               'base': base(request), 'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/add_employee.html'
    return render(request, template, context)


def EmployeePage(request, pk):
    # Fetch all employee's data from database if exists, else 404
    employee = get_object_or_404(Employee, id=pk)
    evaluation = getEvaluation(emp_id=pk)
    # Check if it's CEO page.
    if not isUserAllowedToModify(request.user, employee.position, "CEO"):
        return redirect("Unauthorized")
    # If changing the photo has been requested
    if request.method == 'POST':
        # Get the uploaded image by the user
        img = request.FILES["image_file"]
        # set it for the employee
        q = employee.person
        q.photo = img
        q.save()
        alerts.employee_photo_updated(request)

    context = {'Employee': employee, 'Evaluation': evaluation,
               'base': base(request), 'EmployeeTasks': EmployeeTasks(request)}
    return render(request, 'human_resources/employee.html', context)


def UpdateEmployeePage(request, pk):
    # Getting the employee and person object from database if exists or 404
    employee = get_object_or_404(Employee, id=pk)
    person = Person.objects.get(id=employee.person.id)
    # Check if it's CEO page.
    if not isUserAllowedToModify(request.user, employee.position, "CEO"):
        return redirect("Unauthorized")
    # Setting up the forms
    position_form = EmployeePositionForm(instance=employee)
    person_form = AddPersonForm(instance=person)
    # Check if it is a post method
    if request.method == 'POST':
        person_form = AddPersonForm(request.POST, instance=person)
        position_form = EmployeePositionForm(request.POST, instance=employee)
        # If the forms are valid
        if person_form.is_valid() and position_form.is_valid():
            # Update data
            person_form.save()
            employee.position = position_form['position'].value()
            employee.save()
            alerts.employee_data_updated(request)

            if isRequesterCEO(request):
                return redirect('EmployeePage-CEO', pk)
            else:
                return redirect('EmployeePage', pk)

    context = {'PersonForm': person_form, 'position_form': position_form, 'Employee': employee,
               'base': base(request), 'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/update_employee.html'
    return render(request, template, context)


def DeleteEmployeePage(request, pk):
    # Getting the employee object from database if exists or 404
    employee = get_object_or_404(Employee, id=pk)
    # Check if it is a post method# Check if it's CEO page.
    if not isUserAllowedToModify(request.user, employee.position, "CEO"):
        return redirect("Unauthorized")
    if request.method == "POST":
        # Delete the employee
        employee.delete()
        alerts.employee_removed(request)

        if isRequesterCEO(request):
            return redirect('EmployeesPage-CEO')
        else:
            return redirect('EmployeesPage')

    context = {'Employee': employee, 'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/delete_employee.html'
    return render(request, template, context)


# ------------------------------Distributors------------------------------ #
def DistributorsPage(request):
    # Getting all distributors object from database
    Distributors = Distributor.objects.all().order_by(Lower('person__name'))

    context = {'Distributors': Distributors, 'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/distributors.html'
    return render(request, template, context)


def AddDistributorPage(request):
    # Setting up the form
    person_form = AddPersonForm()
    # Check if it is a post method
    if request.method == 'POST':
        person_form = AddPersonForm(request.POST)
        # If the form is valid
        if person_form.is_valid():
            # Create person
            person_form.save()
            # Create new distributor and a signal will be sent to run onAddingNewDistributor function in signals.py file
            Distributor.objects.create()
            alerts.distributor_added(request)

            if isRequesterCEO(request):
                return redirect('DistributorsPage-CEO')
            else:
                return redirect('DistributorsPage')

    context = {'PersonForm': person_form, 'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/add_distributor.html'
    return render(request, template, context)


def DistributorPage(request, pk):
    # Fetch all distributor's data from database if exists or 404
    distributor = get_object_or_404(Distributor, id=pk)
    # If changing the photo has been requested
    if request.method == 'POST':
        # Get the uploaded image by the user
        img = request.FILES["image_file"]
        # set it for the distributor
        q = distributor.person
        q.photo = img
        q.save()
        alerts.distributor_photo_updated(request)

    context = {'Distributor': distributor, 'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    return render(request, 'human_resources/distributor.html', context)


def UpdateDistributorPage(request, pk):
    # Getting the distributor and person object from database if exists or 404
    distributor = get_object_or_404(Distributor, id=pk)
    person = Person.objects.get(id=distributor.person.id)
    # Setting up the form
    person_form = AddPersonForm(instance=person)
    # Check if it is a post method
    if request.method == 'POST':
        person_form = AddPersonForm(request.POST, instance=person)
        # If the form is valid
        if person_form.is_valid():
            # Update data
            person_form.save()
            alerts.distributor_data_updated(request)

            if isRequesterCEO(request):
                return redirect('DistributorPage-CEO', pk)
            else:
                return redirect('DistributorPage', pk)

    context = {'PersonForm': person_form, 'Distributor': distributor,
               'base': base(request), 'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/update_distributor.html'
    return render(request, template, context)


def DeleteDistributorPage(request, pk):
    # Getting the distributor object from database if exists or 404
    distributor = get_object_or_404(Distributor, id=pk)
    # Check if it is a post method
    if request.method == "POST":
        # Delete the distributor
        distributor.delete()
        alerts.distributor_removed(request)

        if isRequesterCEO(request):
            return redirect('DistributorsPage-CEO')
        else:
            return redirect('DistributorsPage')

    context = {'Distributor': distributor, 'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/delete_distributor.html'
    return render(request, template, context)


# ------------------------------Tasks------------------------------ #
class TasksPage(ListView):

    model = Task
    template_name = 'human_resources/tasks.html'
    context_object_name = 'Tasks'
    ordering = ['-id']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base'] = base(self.request)
        context['EmployeeTasks'] = EmployeeTasks(self.request)
        return context


def AddTaskPage(request):
    # Get the requester position
    requester_position = request.user.groups.all()[0].name
    # Setting up the form
    form = AddTaskForm(requester_position)
    # Check if it is a post method
    if request.method == "POST":
        form = AddTaskForm(requester_position, request.POST)
        # If the form is valid
        if form.is_valid():
            # Add new task
            form.save()
            alerts.Task_added(request)

            if isRequesterCEO(request):
                return redirect('TasksPage-CEO')
            else:
                return redirect('TasksPage')

    context = {'form': form, 'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/add_task.html'
    return render(request, template, context)


def TaskPage(request, pk):
    # Fetch the task's data from database if exists or 404
    task = get_object_or_404(Task, id=pk)
    # Check if the user allowed to view the task page
    if not isUserAllowedToModify(request.user, task.employee.position, "Human Resources"):
        return redirect("Unauthorized")
    # Get the task rate if it exist, else set it to None
    try:
        task_rate = TaskRate.objects.get(task=task)
    except TaskRate.DoesNotExist:
        task_rate = None

    context = {'Task': task, 'TaskRate': task_rate, 'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/task.html'
    return render(request, template, context)


def UpdateTaskPage(request, pk):
    # Fetch the task's data from database if exists or 404
    task = get_object_or_404(Task, id=pk)
    # Check if the user allowed to view the task page
    if not isUserAllowedToModify(request.user, task.employee.position, "Human Resources"):
        return redirect("Unauthorized")
    # Setting up the form
    form = AddTaskForm(request, instance=task)
    # Check if it is a post method
    if request.method == 'POST':
        form = AddTaskForm(request, request.POST, instance=task)
        # If the form is valid
        if form.is_valid():
            # Update
            form.save()
            alerts.Task_data_updated(request)

            if isRequesterCEO(request):
                return redirect('TaskPage-CEO', pk)
            else:
                return redirect('TaskPage', pk)

    context = {'form': form, 'TaskID': task.id, 'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/update_task.html'
    return render(request, template, context)


def DeleteTaskPage(request, pk):
    # Fetch the task's data from database if exists or 404
    task = get_object_or_404(Task, id=pk)
    # Check if the user allowed to view the task page
    if not isUserAllowedToModify(request.user, task.employee.position, "Human Resources"):
        return redirect("Unauthorized")
    # Check if it is a post method
    if request.method == "POST":
        # Delete the task. note: deleteTaskRate function in signals.py will be executed
        task.delete()
        alerts.Task_removed(request)

        if isRequesterCEO(request):
            return redirect('TasksPage-CEO')
        else:
            return redirect('TasksPage')

    context = {'Task': task, 'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/delete_Task.html'
    return render(request, template, context)


# ------------------------------Evaluation------------------------------ #
def EvaluationPage(request):
    # Get the employees Evaluations
    evaluation = getEvaluation()

    context = {'Evaluation': evaluation, 'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/evaluation.html'
    return render(request, template, context)


def WeeklyEvaluationPage(request):
    # Fetch the unrated weeks data from database
    weeks = Week.objects.filter(is_rated=False)

    context = {'week_to_rate_exists': True, 'base': base(
        request), 'EmployeeTasks': EmployeeTasks(request)}
    # if there is no unrated weeks, just send a success message
    if not weeks.exists():
        alerts.evaluation_done(request)
        context['week_to_rate_exists'] = False
    else:
        # Fetch the employees' data from database excluding the HR and CEO
        Employees = Employee.objects.filter(~Q(position="CEO") &
                                            ~Q(position="Human Resources"))
        context['Employees'] = Employees
        # if there is more than one unrated weeks
        if len(weeks) > 1:
            unrated_weeks_to_delete = 0
            for index, week in enumerate(weeks):
                # if it is the last week, send the following messages only
                if index == len(weeks) - 1:
                    alerts.many_weeks(request)
                    alerts.deleted_weeks(request, unrated_weeks_to_delete)
                    alerts.inform_ceo(request)
                # else delete the week
                else:
                    week.delete()
                    unrated_weeks_to_delete += 1
        # Check if it is a post method
        if request.method == "POST":
            # get the employees rate from the user and create a weekly rate for each employee
            for emp in Employees:
                val = request.POST.get(f'val{str(emp.id)}', False)
                # Rate employees
                WeeklyRate.objects.create(
                    week=weeks[0],
                    employee=emp,
                    rate=int(val))
            # Rate HR by his/her last week tasks rate
            hr = Employee.objects.get(position="Human Resources")
            WeeklyRate.objects.create(
                week=weeks[0],
                employee=hr,
                rate=getTaskRateFrom(hr.id, 7))

            # change the week state
            weeks[0].is_rated = True
            weeks[0].save()

            try:
                # change the last weekly evaluations task state
                task = Task.objects.get(
                    name="Evaluate employees", is_rated=False)
                task.status = "On-Time"
                task.submission_date = timezone.now()
                task.is_rated = True
                task.save()
                # Rate the task automatically
                TaskRate.objects.create(task=task, on_time_rate=5, rate=5)
            except Task.DoesNotExist:
                pass

            if isRequesterCEO(request):
                return redirect('EvaluationPage-CEO')
            else:
                return redirect('EvaluationPage')

    template = 'human_resources/weekly_rate.html'
    return render(request, template, context)


def TaskEvaluationPage(request):
    # Fetch the submitted tasks data from database
    if isRequesterCEO:
        Tasks = Task.objects.filter(~Q(status="In-Progress") &
                                    ~Q(status="Overdue"), is_rated=False
                                    ).order_by(Lower('employee__person__name'))
    else:
        Tasks = Task.objects.filter(~Q(status="In-Progress") & ~Q(status="Overdue"),
                                    ~Q(employee__position="Human Resources"),
                                    is_rated=False).order_by(Lower('employee__person__name'))
    # Check if it is a post method
    if request.method == "POST":
        # Get the posted (rated) task id
        id = request.POST.get('id', False)
        # Get the value of the posted task rate
        val = request.POST.get(f'val{str(id)}', False)
        # Fetch the task from database and calculate 'on time rate'
        task = Task.objects.get(id=int(id))
        on_time = 5
        if task.status != "On-Time":
            on_time = 2.5
        # Rate the task
        TaskRate.objects.create(
            task=task, on_time_rate=on_time, rate=float(val))
        task.is_rated = True
        task.save()
        # Get the auto task for the HR and process it
        if not isRequesterCEO:
            auto_task = Task.objects.get(
                employee__position="Human Resources",
                description=f"Don't forget to rate {task.employee.person.name}'s submitted task. '{task.name}' Task.",
                is_rated=False)
            # Check if the HR rate the task on time
            on_time = 5
            status = 'On-Time'
            if auto_task.status != 'In-Progress':
                on_time = 2.5
                status = 'Late-Submission'
            # Rate the task automatically
            TaskRate.objects.create(
                task=auto_task, on_time_rate=on_time, rate=float(5))
            auto_task.status = status
            auto_task.is_rated = True
            auto_task.submission_date = timezone.now()
            auto_task.save()
        # Success message
        alerts.tasks_evaluation_done(request)
    # If there is no tasks to rate just send a message
    if not Tasks.exists():
        alerts.no_tasks_to_rate(request)

    context = {'Tasks': Tasks,  'base': base(request),
               'EmployeeTasks': EmployeeTasks(request)}
    template = 'human_resources/task_evaluation.html'
    return render(request, template, context)
