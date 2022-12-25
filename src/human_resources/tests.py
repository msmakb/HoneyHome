from typing import Any

from django.contrib.auth.models import Group, User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse, resolve
from django.utils import timezone
from django.utils.timezone import datetime

from main import constants
from main.models import Person
from main.views import tasks, index

from distributor.models import Distributor

from . import views
from .cron import addWeekToRate, checkTasksStatus
from .evaluation import (monthlyRate, getTaskRateFrom, monthlyTaskRate,
                         weeklyRate, monthlyOverallEvaluation, allTimeEvaluation,
                         getEvaluation, allEmployeesWeeklyEvaluations,
                         allEmployeesMonthlyEvaluations, allEmployeesMonthlyTaskRate,
                         allEmployeesMonthlyOverallEvaluation)
from .forms import AddPersonForm, EmployeeForm, AddTaskForm
from .models import Employee, Task, TaskRate, Week, WeeklyRate
from .utils import isRequesterCEO, isUserAllowedToModify


class TestCron(TestCase):

    def test_cron_add_week_to_rate(self) -> None:
        self.assertEquals(Week.objects.count(), 0)
        addWeekToRate()
        self.assertEquals(Week.objects.count(), 0)  # no HR
        employee: Employee = Employee.objects.create(
            person=Person.objects.create(name="TEST"),
            position=constants.ROLES.HUMAN_RESOURCES
        )
        addWeekToRate()
        self.assertEquals(Task.objects.filter(employee=employee).count(), 1)
        self.assertEquals(Week.objects.count(), 1)
        addWeekToRate()
        self.assertEquals(Task.objects.filter(employee=employee).count(), 1)
        self.assertEquals(Week.objects.count(), 1)
        week: Week = Week.objects.first()
        week.week_end_date = timezone.now() - timezone.timedelta(days=7)
        week.save()
        addWeekToRate()
        self.assertEquals(Task.objects.filter(employee=employee).count(), 2)
        self.assertEquals(Week.objects.count(), 2)

    def test_cron_check_tasks_status(self) -> None:
        task: Task = Task.objects.create(
            employee=Employee.objects.first(),
            task="TEST",
            description="Test",
            deadline_date=timezone.now() - timezone.timedelta(seconds=50)
        )
        checkTasksStatus()
        task: Task = Task.objects.get(id=task.id)
        self.assertEquals(task.status, constants.TASK_STATUS.OVERDUE)

        task: Task = Task.objects.create(
            employee=Employee.objects.first(),
            task="TEST",
            description="Test",
            deadline_date=timezone.now() + timezone.timedelta(seconds=50)
        )
        checkTasksStatus()
        task: Task = Task.objects.get(id=task.id)
        self.assertEquals(task.status, constants.TASK_STATUS.IN_PROGRESS)

        task: Task = Task.objects.create(
            employee=Employee.objects.first(),
            task="TEST",
            description="Test",
            deadline_date=timezone.now() + timezone.timedelta(days=3)
        )
        checkTasksStatus()
        task: Task = Task.objects.get(id=task.id)
        self.assertEquals(task.status, constants.TASK_STATUS.IN_PROGRESS)

        task: Task = Task.objects.create(
            employee=Employee.objects.first(),
            task="TEST",
            description="Test",
            deadline_date=timezone.now() - timezone.timedelta(days=3)
        )
        checkTasksStatus()
        task: Task = Task.objects.get(id=task.id)
        self.assertEquals(task.status, constants.TASK_STATUS.OVERDUE)
        task.setDeadlineDate("TEST", timezone.now() +
                             timezone.timedelta(days=3))
        checkTasksStatus()
        task: Task = Task.objects.get(id=task.id)
        self.assertEquals(task.status, constants.TASK_STATUS.IN_PROGRESS)

        task: Task = Task.objects.create(
            employee=Employee.objects.first(),
            task="TEST",
            description="Test",
            deadline_date=timezone.now() - timezone.timedelta(days=3)
        )
        task.setStatus("TESTER", constants.TASK_STATUS.ON_TIME)
        checkTasksStatus()
        task: Task = Task.objects.get(id=task.id)
        self.assertEquals(task.status, constants.TASK_STATUS.ON_TIME)

        task: Task = Task.objects.create(
            employee=Employee.objects.first(),
            task="TEST",
            description="Test",
            deadline_date=timezone.now() - timezone.timedelta(days=3)
        )
        task.setStatus("TESTER", constants.TASK_STATUS.LATE_SUBMISSION)
        checkTasksStatus()
        task: Task = Task.objects.get(id=task.id)
        self.assertEquals(task.status, constants.TASK_STATUS.LATE_SUBMISSION)


class TestEvaluationModule(TestCase):

    def setUp(self) -> None:
        self.employee: Employee = Employee.objects.all().first()

    def test_monthly_rate(self) -> None:
        self.assertEquals(monthlyRate(self.employee.id), 0)
        week: Week = Week.objects.create(
            week_start_date=timezone.now().date(),
            week_end_date=timezone.now().date(),
            is_rated=True
        )
        WeeklyRate.objects.create(
            week=week,
            employee=self.employee,
            rate=3.00
        )
        self.assertEquals(monthlyRate(self.employee.id), 3.00)
        WeeklyRate.objects.create(
            week=week,
            employee=self.employee,
            rate=5.00
        )
        self.assertEquals(monthlyRate(self.employee.id), 4.00)
        for i in range(3):
            WeeklyRate.objects.create(
                week=week,
                employee=self.employee,
                rate=3.00
            )
        self.assertEquals(monthlyRate(self.employee.id), 3.50)

    def test_get_task_rate_from_period(self) -> None:
        TaskRate.objects.create(
            task=Task.objects.create(
                task="test",
                employee=self.employee,
                description="Noting",
            ),
            on_time_rate=2.5,
            rate=4.45
        )
        self.assertEquals(getTaskRateFrom(self.employee.id, 1), 3.48)
        TaskRate.objects.create(
            task=Task.objects.create(
                task="test",
                employee=self.employee,
                description="Noting",
            ),
            on_time_rate=5,
            rate=3.82
        )
        self.assertEquals(getTaskRateFrom(self.employee.id, 1), 3.94)
        task_rate: TaskRate = TaskRate.objects.create(
            task=Task.objects.create(
                task="test",
                employee=self.employee,
                description="Noting",
            ),
            on_time_rate=5,
            rate=5
        )
        task_rate.created = timezone.now() - timezone.timedelta(days=1, milliseconds=1)
        task_rate.save()
        self.assertEquals(getTaskRateFrom(self.employee.id, 1), 3.94)

    def test_monthly_task_rate(self) -> None:
        self.assertEquals(TaskRate.objects.all().count(), 0)
        for _ in range(10):
            TaskRate.objects.create(
                task=Task.objects.create(
                    task="test",
                    employee=self.employee,
                    description="Noting",
                ),
                on_time_rate=2.5,
                rate=4.5
            )
        task_rate: TaskRate = TaskRate.objects.create(
            task=Task.objects.create(
                task="test",
                employee=self.employee,
                description="Noting",
            ),
            on_time_rate=5,
            rate=5
        )
        task_rate.created = timezone.now() - timezone.timedelta(days=30, milliseconds=1)
        task_rate.save()
        self.assertEquals(monthlyTaskRate(self.employee.id), 3.50)

    def test_get_weekly_rate(self) -> None:
        self.assertEquals(WeeklyRate.objects.all().count(), 0)
        self.assertEquals(weeklyRate(self.employee.id), 0)
        for _ in range(3):
            week: Week = Week.objects.create(
                week_start_date=timezone.now().date(),
                week_end_date=timezone.now().date(),
                is_rated=True
            )
            week.created = timezone.now() - timezone.timedelta(milliseconds=10)
            week.save()
            WeeklyRate.objects.create(
                week=week,
                employee=self.employee,
                rate=5
            )
        WeeklyRate.objects.create(
            week=Week.objects.create(
                week_start_date=timezone.now().date(),
                week_end_date=timezone.now().date(),
                is_rated=True
            ),
            employee=self.employee,
            rate=3.14
        )
        self.assertEquals(weeklyRate(self.employee.id), 3.14)

    def test_monthly_overall_evaluation(self) -> None:
        self.assertEquals(TaskRate.objects.all().count(), 0)
        self.assertEquals(WeeklyRate.objects.all().count(), 0)
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=Week.objects.create(
                week_start_date=timezone.now().date(),
                week_end_date=timezone.now().date(),
                is_rated=True
            ),
            employee=self.employee,
            rate=3.50
        )
        weekly_rate.created = timezone.now() - timezone.timedelta(days=25)
        weekly_rate.save()
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=Week.objects.create(
                week_start_date=timezone.now().date(),
                week_end_date=timezone.now().date(),
                is_rated=True
            ),
            employee=self.employee,
            rate=4.00
        )
        weekly_rate.created = timezone.now() - timezone.timedelta(days=31)
        weekly_rate.save()
        task_rate: TaskRate = TaskRate.objects.create(
            task=Task.objects.create(
                task="test",
                employee=self.employee,
                description="Noting",
            ),
            on_time_rate=2.50,
            rate=3.50
        )
        task_rate.created = timezone.now() - timezone.timedelta(days=4)
        task_rate.save()
        self.assertEquals(monthlyOverallEvaluation(self.employee.id), 3.25)

    def test_all_time_overall_evaluation(self) -> None:
        self.assertEquals(TaskRate.objects.all().count(), 0)
        self.assertEquals(WeeklyRate.objects.all().count(), 0)
        WeeklyRate.objects.create(
            week=Week.objects.create(
                week_start_date=timezone.now().date(),
                week_end_date=timezone.now().date(),
                is_rated=True
            ),
            employee=self.employee,
            rate=4.50
        )
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=Week.objects.create(
                week_start_date=timezone.now().date(),
                week_end_date=timezone.now().date(),
                is_rated=True
            ),
            employee=self.employee,
            rate=3.50
        )
        weekly_rate.created = timezone.now() - timezone.timedelta(days=1000)
        weekly_rate.save()
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=Week.objects.create(
                week_start_date=timezone.now().date(),
                week_end_date=timezone.now().date(),
                is_rated=True
            ),
            employee=self.employee,
            rate=4.00
        )
        weekly_rate.created = timezone.now() - timezone.timedelta(days=250)
        weekly_rate.save()
        task_rate: TaskRate = TaskRate.objects.create(
            task=Task.objects.create(
                task="test",
                employee=self.employee,
                description="Noting",
            ),
            on_time_rate=2.50,
            rate=3.50
        )
        task_rate.created = timezone.now() - timezone.timedelta(days=15)
        task_rate.save()
        self.assertEquals(allTimeEvaluation(self.employee.id), 3.50)

    def test_get_evaluation(self) -> None:
        self.assertEquals(TaskRate.objects.all().count(), 0)
        self.assertEquals(WeeklyRate.objects.all().count(), 0)
        WeeklyRate.objects.create(
            week=Week.objects.create(
                week_start_date=timezone.now().date(),
                week_end_date=timezone.now().date(),
                is_rated=True
            ),
            employee=self.employee,
            rate=4.00
        )
        week: Week = Week.objects.create(
            week_start_date=timezone.now().date(),
            week_end_date=timezone.now().date(),
            is_rated=True
        )
        week.created = timezone.now() - timezone.timedelta(days=25)
        week.save()
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=week,
            employee=self.employee,
            rate=3.00
        )
        weekly_rate.created = timezone.now() - timezone.timedelta(days=25)
        weekly_rate.save()
        task_rate: TaskRate = TaskRate.objects.create(
            task=Task.objects.create(
                task="test",
                employee=self.employee,
                description="Noting",
            ),
            on_time_rate=2.50,
            rate=3.50
        )
        task_rate.created = timezone.now() - timezone.timedelta(days=5)
        task_rate.save()
        week: Week = Week.objects.create(
            week_start_date=timezone.now().date(),
            week_end_date=timezone.now().date(),
            is_rated=True
        )
        week.created = timezone.now() - timezone.timedelta(days=50)
        week.save()
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=week,
            employee=self.employee,
            rate=5.00
        )
        weekly_rate.created = timezone.now() - timezone.timedelta(days=50)
        weekly_rate.save()
        task_rate: TaskRate = TaskRate.objects.create(
            task=Task.objects.create(
                task="test",
                employee=self.employee,
                description="Noting",
            ),
            on_time_rate=5.00,
            rate=5.00
        )
        task_rate.created = timezone.now() - timezone.timedelta(days=50)
        task_rate.save()

        employee_evaluation: dict[str, Employee | float] = getEvaluation(
            emp_id=self.employee.id)

        self.assertEquals(type(employee_evaluation), dict)
        self.assertIn("Employee", employee_evaluation)
        self.assertEquals(type(employee_evaluation["Employee"]), Employee)
        self.assertEquals(employee_evaluation["Employee"].id, self.employee.id)
        self.assertIn("MonthlyRate", employee_evaluation)
        self.assertEquals(employee_evaluation["MonthlyRate"], 3.50)
        self.assertIn("WeeklyRate", employee_evaluation)
        self.assertEquals(employee_evaluation["WeeklyRate"], 4.00)
        self.assertIn("MonthlyTaskRate", employee_evaluation)
        self.assertEquals(employee_evaluation["MonthlyTaskRate"], 3.00)
        self.assertIn("MonthlyOverallEvaluation", employee_evaluation)
        self.assertEquals(
            employee_evaluation["MonthlyOverallEvaluation"], 3.25)
        self.assertIn("AllTimeEvaluation", employee_evaluation)
        self.assertEquals(employee_evaluation["AllTimeEvaluation"], 4.00)

    def test_all_employees_weekly_evaluations(self) -> None:
        self.assertEquals(allEmployeesWeeklyEvaluations(), 0)
        hr: Employee = Employee.objects.create(
            person=Person.objects.create(name="HR"),
            position=constants.ROLES.HUMAN_RESOURCES)
        am: Employee = Employee.objects.create(
            person=Person.objects.create(name="AM"),
            position=constants.ROLES.ACCOUNTING_MANAGER)
        wa: Employee = Employee.objects.create(
            person=Person.objects.create(name="WA"),
            position=constants.ROLES.WAREHOUSE_ADMIN)
        week: Week = Week.objects.create(
            week_start_date=timezone.now().date(),
            week_end_date=timezone.now().date(),
            is_rated=True
        )
        week.created = timezone.now() - timezone.timedelta(days=7)
        week.save()
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=week,
            employee=hr,
            rate=3.00
        )
        weekly_rate.created = timezone.now() - timezone.timedelta(days=7)
        weekly_rate.save()
        week: Week = Week.objects.create(
            week_start_date=timezone.now().date(),
            week_end_date=timezone.now().date(),
            is_rated=True
        )
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=week,
            employee=hr,
            rate=4.00
        )
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=week,
            employee=am,
            rate=4.50
        )
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=week,
            employee=wa,
            rate=4.00
        )
        self.assertEquals(allEmployeesWeeklyEvaluations(), 4.17)

    def test_all_employees_monthly_evaluations_for_weekly_rate_and_task_rate_and_overall_rate(self) -> None:
        self.assertEquals(allEmployeesMonthlyEvaluations(), 0)
        self.assertEquals(allEmployeesMonthlyTaskRate(), 0)
        self.assertEquals(allEmployeesMonthlyOverallEvaluation(), 0)
        hr: Employee = Employee.objects.create(
            person=Person.objects.create(name="HR"),
            position=constants.ROLES.HUMAN_RESOURCES)
        am: Employee = Employee.objects.create(
            person=Person.objects.create(name="AM"),
            position=constants.ROLES.ACCOUNTING_MANAGER)
        wa: Employee = Employee.objects.create(
            person=Person.objects.create(name="WA"),
            position=constants.ROLES.WAREHOUSE_ADMIN)
        week: Week = Week.objects.create(
            week_start_date=timezone.now().date(),
            week_end_date=timezone.now().date(),
            is_rated=True
        )
        week.created = timezone.now() - timezone.timedelta(days=7)
        week.save()
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=week,
            employee=hr,
            rate=3.00
        )
        weekly_rate.created = timezone.now() - timezone.timedelta(days=7)
        weekly_rate.save()
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=week,
            employee=am,
            rate=3.50
        )
        weekly_rate.created = timezone.now() - timezone.timedelta(days=7)
        weekly_rate.save()
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=week,
            employee=wa,
            rate=4.50
        )
        weekly_rate.created = timezone.now() - timezone.timedelta(days=7)
        weekly_rate.save()
        week: Week = Week.objects.create(
            week_start_date=timezone.now().date(),
            week_end_date=timezone.now().date(),
            is_rated=True
        )
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=week,
            employee=hr,
            rate=4.00
        )
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=week,
            employee=am,
            rate=4.50
        )
        weekly_rate: WeeklyRate = WeeklyRate.objects.create(
            week=week,
            employee=wa,
            rate=4.00
        )
        task_rate: TaskRate = TaskRate.objects.create(
            task=Task.objects.create(
                task="test",
                employee=hr,
                description="Noting",
            ),
            on_time_rate=5.00,
            rate=4.50
        )
        task_rate.created = timezone.now() - timezone.timedelta(days=5)
        task_rate.save()
        task_rate: TaskRate = TaskRate.objects.create(
            task=Task.objects.create(
                task="test",
                employee=am,
                description="Noting",
            ),
            on_time_rate=3.50,
            rate=3.50
        )
        task_rate.created = timezone.now() - timezone.timedelta(days=15)
        task_rate.save()
        task_rate: TaskRate = TaskRate.objects.create(
            task=Task.objects.create(
                task="test",
                employee=wa,
                description="Noting",
            ),
            on_time_rate=2.50,
            rate=4.50
        )
        task_rate: TaskRate = TaskRate.objects.create(
            task=Task.objects.create(
                task="test",
                employee=wa,
                description="Noting",
            ),
            on_time_rate=5.00,
            rate=5.00
        )
        task_rate.created = timezone.now() - timezone.timedelta(days=31)
        task_rate.save()

        self.assertEquals(allEmployeesMonthlyEvaluations(), 3.92)
        self.assertEquals(allEmployeesMonthlyTaskRate(), 3.92)
        self.assertEquals(allEmployeesMonthlyOverallEvaluation(), 3.92)


class TestForms(TestCase):

    def setUp(self) -> None:
        self.request: HttpRequest = HttpRequest()
        self.request.user: User = User.objects.all().first()
        self.hr_user, created = User.objects.get_or_create(username="Test HR")
        self.hr_user.first_name = "Test"
        self.hr_user.last_name = "HR"
        self.hr_user.groups.clear()
        Group.objects.get(name=constants.ROLES.HUMAN_RESOURCES
                          ).user_set.add(self.hr_user)

    def test_add_person_form(self) -> None:
        data: dict[str, Any] = {}
        form = AddPersonForm(self.request, data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 5)
        data["name"] = "INVALID VERY LONG NAME" * 10
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 5)
        data["name"] = "Form Tester"
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 4)
        data["gender"] = "Not valid choice"
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 4)
        data["gender"] = constants.GENDER.MALE
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 3)
        data["nationality"] = "Not valid choice"
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 3)
        data["nationality"] = constants.COUNTRY.get("YEMEN")
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 2)
        data["contacting_email"] = "invalidEmail"
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 2)
        data["contacting_email"] = "valid@email.com"
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 1)
        data["date_of_birth"] = "invalid Date"
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 2)
        data["date_of_birth"] = timezone.now()
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 1)
        data["address"] = "Very Long Address!" * 15
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 2)
        data["address"] = "Python Street No.1"
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 1)
        data["phone_number"] = "1 123123123123"  # No + in the beginning
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 1)
        data["phone_number"] = "+1 123123123123A"  # Not all int
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 1)
        # country key and number are not separated
        data["phone_number"] = "+1123123123123"
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 1)
        # country Key has more than 3 numbers
        data["phone_number"] = "+1234 123123123123"
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 1)
        data["phone_number"] = "+ 123123123123"  # No key
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 1)
        data["phone_number"] = "+1 12345678"  # lees than 8 nm
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 1)
        data["phone_number"] = "+1 123456789012345"  # mor than 14 nm
        form = AddPersonForm(self.request, data=data)
        self.assertEquals(len(form.errors), 1)
        data["phone_number"] = "+1 123456789"  # valid
        form = AddPersonForm(self.request, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        person: Person = Person.objects.all().last()
        self.assertEquals(person.created_by, self.request.user.get_full_name())
        self.assertEquals(person.updated_by, self.request.user.get_full_name())

    def test_employee_form(self) -> None:
        data: dict[str, Any] = {}
        form = EmployeeForm(self.request, data=data)
        self.assertFalse(form.is_valid())
        data["position"] = "Invalid Role"
        form = EmployeeForm(self.request, data=data)
        self.assertFalse(form.is_valid())
        data["position"] = constants.ROLES.CEO  # exist role
        form = EmployeeForm(self.request, data=data)
        self.assertFalse(form.is_valid())
        self.request.user = self.hr_user
        data["position"] = constants.ROLES.CEO  # HR trying to add CEO
        form = EmployeeForm(self.request, data=data)
        self.assertFalse(form.is_valid())
        # valid (HR adding AM)
        data["position"] = constants.ROLES.ACCOUNTING_MANAGER
        form = EmployeeForm(self.request, data=data)
        self.assertTrue(form.is_valid())
        Person.objects.create(name="Test employee form")
        form.save()
        employee: Employee = Employee.objects.all().last()
        self.assertEquals(employee.person.name, "Test employee form")
        self.assertEquals(employee.created_by, "Test HR")
        self.assertEquals(employee.updated_by, "Test HR")

    def test_add_task_form(self) -> None:
        data: dict[str, Any] = {"description": "-"}
        form = AddTaskForm(self.request, data=data)
        employee: Employee = Employee.objects.create(
            person=Person.objects.create(name="Test"),
            account=self.hr_user,
            position=constants.ROLES.HUMAN_RESOURCES)
        self.assertFalse(form.is_valid())
        data["employee"] = Employee.objects.all().first()  # assign task to CEO
        form = AddTaskForm(self.request, data=data)
        self.assertFalse(form.is_valid())
        # assign task to HR as CEO
        data["employee"] = employee
        form = AddTaskForm(self.request, data=data)
        self.assertFalse("employee" in form.errors)
        self.request.user = employee.account
        data["employee"] = employee  # HR assigning task to himself
        form = AddTaskForm(self.request, data=data)
        self.assertTrue("employee" in form.errors)
        # HR assigning task to someone else (valid)
        employee.position = constants.ROLES.ACCOUNTING_MANAGER
        employee.save()
        data["employee"] = employee
        form = AddTaskForm(self.request, data=data)
        self.assertFalse("employee" in form.errors)
        data["task"] = "Very long task name" * 10
        form = AddTaskForm(self.request, data=data)
        self.assertTrue("task" in form.errors)
        data["task"] = "Valid task name"
        form = AddTaskForm(self.request, data=data)
        self.assertTrue(form.is_valid())
        # Test deadline date more than a month
        data["deadline_date"] = timezone.now(
        ) + timezone.timedelta(days=30, milliseconds=50)
        form = AddTaskForm(self.request, data=data)
        self.assertFalse(form.is_valid())
        # Test deadline date lees than an hour
        data["deadline_date"] = timezone.now(
        ) + timezone.timedelta(minutes=59)
        form = AddTaskForm(self.request, data=data)
        self.assertFalse(form.is_valid())
        data["deadline_date"] = timezone.now(
        ) + timezone.timedelta(hours=2)
        form = AddTaskForm(self.request, data=data)
        self.assertTrue(form.is_valid())


class TestModels(TestCase):

    def test_task_model_time_lift(self) -> None:
        now: datetime = timezone.now()
        task: Task = Task.objects.create(
            employee=Employee.objects.all().first(),
            task="Test time lift",
            deadline_date=(now + timezone.timedelta(minutes=5)),
        )
        almost_equals: bool = lambda first, second: any((first == second,
                                                         first + 1 == second,
                                                         first == 1 + second))
        time_lift_in_seconds: int = lambda task: sum(
            x * int(t) for x, t in zip([3600, 60, 1], task.time_left.split(":")))
        self.assertTrue(almost_equals(time_lift_in_seconds(task),
                                      timezone.timedelta(minutes=5).total_seconds()))
        task.deadline_date = now + timezone.timedelta(hours=10)
        task.save()
        self.assertTrue(almost_equals(time_lift_in_seconds(task),
                                      timezone.timedelta(hours=10).total_seconds()))
        task.deadline_date = now + \
            timezone.timedelta(hours=6, minutes=35, seconds=40)
        task.save()
        self.assertTrue(almost_equals(time_lift_in_seconds(task),
                                      timezone.timedelta(hours=6, minutes=35,
                                                         seconds=40).total_seconds()))
        task.deadline_date = now
        task.save()
        self.assertEquals(task.time_left, 'Overdue')
        task.deadline_date = None
        task.save()
        self.assertEquals(task.time_left, 'Open')
        task.submission_date = now
        task.save()
        self.assertEquals(task.time_left, 'Submitted')


class TestSignals(TestCase):

    def test_on_adding_updating_employee_signal(self) -> None:
        Person.objects.create(name="TEST SIGNAL")
        employee: Employee = Employee.objects.create(
            position=constants.ROLES.ACCOUNTING_MANAGER
        )
        self.assertFalse(employee.account.is_superuser)
        self.assertEquals(employee.person.name, "TEST SIGNAL")
        self.assertEquals(employee.account.username, "TEST")
        self.assertEquals(employee.account.get_full_name(), "TEST SIGNAL")
        self.assertEquals(employee.account.groups.first().name,
                          constants.ROLES.ACCOUNTING_MANAGER)

        employee.position = constants.ROLES.HUMAN_RESOURCES
        employee.save()

        self.assertEquals(employee.account.groups.count(), 1)
        self.assertEquals(employee.position, constants.ROLES.HUMAN_RESOURCES)
        self.assertEquals(employee.account.groups.first().name,
                          constants.ROLES.HUMAN_RESOURCES)

    def test_on_adding_updating_employee_signal(self) -> None:
        Person.objects.create(name="TEST SIGNAL")
        distributor: Distributor = Distributor.objects.create()

        self.assertFalse(distributor.account.is_superuser)
        self.assertIsNotNone(distributor.stock)
        self.assertEquals(distributor.person.name, "TEST SIGNAL")
        self.assertEquals(distributor.account.username, "TEST")
        self.assertEquals(distributor.account.get_full_name(), "TEST SIGNAL")
        self.assertEquals(distributor.account.groups.first().name,
                          constants.ROLES.DISTRIBUTOR)

    def test_delete_user_account_after_deleting_employee_or_distributor_object(self) -> None:
        Person.objects.create(name="TEST SIGNAL")
        employee: Employee = Employee.objects.create(
            position=constants.ROLES.SOCIAL_MEDIA_MANAGER
        )
        self.assertIsNotNone(employee.account)
        account_id = employee.account.id
        self.assertEquals(User.objects.get(id=account_id).username, "TEST")
        employee.delete("TEST")
        self.assertRaises(User.DoesNotExist, User.objects.get, id=account_id)

        Person.objects.create(name="TEST SIGNAL")
        distributor: Distributor = Distributor.objects.create()
        self.assertIsNotNone(distributor.account)
        account_id = distributor.account.id
        self.assertEquals(User.objects.get(id=account_id).username, "TEST")
        distributor.delete("TEST")
        self.assertRaises(User.DoesNotExist, User.objects.get, id=account_id)

    def test_delete_task_rate_after_task_been_deleted(self) -> None:
        task: Task = Task.objects.create(
            task="test",
            employee=Employee.objects.first(),
            description="Noting",
        )
        task_rate: TaskRate = TaskRate.objects.create(
            task=task,
            on_time_rate=5.00,
            rate=5.00
        )
        task_rate_id = task_rate.id
        self.assertIsNotNone(TaskRate.objects.get(id=task_rate_id))
        task.delete("TEST")
        self.assertRaises(TaskRate.DoesNotExist,
                          TaskRate.objects.get,
                          id=task_rate_id)


class TestUrls(TestCase):

    def setUp(self) -> None:
        Task.objects.create(employee=Employee.objects.first())
        Distributor.objects.create(person=Person.objects.create(name="test"))

    def test_human_resources_dashboard_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.HUMAN_RESOURCES_DASHBOARD)
        self.assertEquals(resolve(url).func, views.humanResourcesDashboard)

    def test_employees_list_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.EMPLOYEES_PAGE)
        self.assertEquals(resolve(url).func, views.employeesPage)

    def test_add_employee_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.ADD_EMPLOYEE_PAGE)
        self.assertEquals(resolve(url).func, views.addEmployeePage)

    def test_employee_record_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.EMPLOYEE_RECORD_PAGE,
                           args=['1'])
        self.assertEquals(resolve(url).func, views.employeePage)

    def test_update_employee_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.UPDATE_EMPLOYEE_PAGE,
                           args=['1'])
        self.assertEquals(resolve(url).func, views.updateEmployeePage)

    def test_delete_employee_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.DELETE_EMPLOYEE_PAGE,
                           args=['1'])
        self.assertEquals(resolve(url).func, views.deleteEmployeePage)

    def test_distributors_list_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.DISTRIBUTORS_PAGE)
        self.assertEquals(resolve(url).func, views.distributorsPage)

    def test_add_distributor_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.ADD_DISTRIBUTOR_PAGE)
        self.assertEquals(resolve(url).func, views.addDistributorPage)

    def test_distributor_record_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.DISTRIBUTOR_RECORD_PAGE,
                           args=['1'])
        self.assertEquals(resolve(url).func, views.distributorPage)

    def test_update_distributor_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.UPDATE_DISTRIBUTOR_PAGE,
                           args=['1'])
        self.assertEquals(resolve(url).func, views.updateDistributorPage)

    def test_delete_distributor_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.DELETE_DISTRIBUTOR_PAGE,
                           args=['1'])
        self.assertEquals(resolve(url).func, views.deleteDistributorPage)

    def test_employee_tasks_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.EMPLOYEES_TASKS_PAGE)
        self.assertEquals(resolve(url).func, views.employeeTasksPage)

    def test_add_task_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.ADD_TASK_PAGE)
        self.assertEquals(resolve(url).func, views.addTaskPage)

    def test_detailed_task_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.DETAILED_TASK_PAGE,
                           args=['1'])
        self.assertEquals(resolve(url).func, views.taskPage)

    def test_update_task_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.UPDATE_TASK_PAGE,
                           args=['1'])
        self.assertEquals(resolve(url).func, views.updateTaskPage)

    def test_delete_task_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.DELETE_TASK_PAGE,
                           args=['1'])
        self.assertEquals(resolve(url).func, views.deleteTaskPage)

    def test_evaluation_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.EVALUATION_PAGE)
        self.assertEquals(resolve(url).func, views.evaluationPage)

    def test_weekly_evaluation_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.WEEKLY_EVALUATION_PAGE)
        self.assertEquals(resolve(url).func, views.weeklyEvaluationPage)

    def test_task_evaluation_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.TASK_EVALUATION_PAGE)
        self.assertEquals(resolve(url).func, views.taskEvaluationPage)

    def test_task_page_is_resolved(self) -> None:
        url: str = reverse("human_resources:" +
                           constants.PAGES.TASKS_PAGE)
        self.assertEquals(resolve(url).func, tasks)


class TestUtils(TestCase):

    def setUp(self) -> None:
        self.user: User = User.objects.create_superuser("TestUser")
        Group.objects.get(name=constants.ROLES.CEO
                          ).user_set.add(self.user)

    def test_is_requester_is_ceo(self) -> None:
        request: HttpRequest = HttpRequest()
        request.user: User = self.user
        self.assertTrue(isRequesterCEO(request))
        request.user.groups.clear()
        Group.objects.get(name=constants.ROLES.HUMAN_RESOURCES
                          ).user_set.add(request.user)
        self.assertFalse(isRequesterCEO(request))

    def test_is_user_allowed_to_modify(self) -> None:

        self.assertTrue(isUserAllowedToModify(self.user, constants.ROLES.CEO,
                                              constants.ROLES.CEO))
        self.user.groups.clear()
        Group.objects.get(name=constants.ROLES.HUMAN_RESOURCES
                          ).user_set.add(self.user)
        self.assertFalse(isUserAllowedToModify(self.user, constants.ROLES.HUMAN_RESOURCES,
                                               constants.ROLES.HUMAN_RESOURCES))
        self.assertFalse(isUserAllowedToModify(self.user, constants.ROLES.CEO,
                                               constants.ROLES.CEO))

    def tearDown(self) -> None:
        self.user.delete()
        return super().tearDown()


class TestViews(TestCase):

    def setUp(self) -> None:
        self.client = RequestFactory()
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"
        self.client.defaults['REMOTE_ADDR'] = self.test_ip
        self.client.defaults['HTTP_USER_AGENT'] = self.user_agent
        Person.objects.create(name="HR")
        self.employee: Employee = Employee.objects.create(
            position=constants.ROLES.HUMAN_RESOURCES)
        self.request: HttpRequest = self.client.get('/')
        self.request.user = self.employee.account
        self.hr_pages = 'HumanResources:'

        self.add_session()

    def add_session(self) -> None:
        setattr(self.request, 'session', 'session')
        setattr(self.request, '_messages', FallbackStorage(self.request))
        session_middleware = SessionMiddleware(lambda request: None)
        session_middleware.process_request(self.request)
        self.request.session.save()

    def test_human_resources_dashboard(self) -> None:
        response: HttpResponse = views.humanResourcesDashboard(self.request)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)
        # Index page redirects the HR to his dashboard
        response: HttpResponse = index(self.request)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)

    def test_employees_page(self) -> None:
        response: HttpResponse = views.employeesPage(self.request)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

    def test_add_employee_page(self) -> None:
        response: HttpResponse = views.addEmployeePage(self.request)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

        self.request = self.client.post('/', {
            'name': 'Test123',
            'gender': constants.GENDER.MALE,
            'nationality': constants.COUNTRY.get('YEMEN'),
            'date_of_birth': timezone.datetime(year=1999, month=12, day=12).date(),
            'contacting_email': 'test@test.te',
            'phone_number': '+123 123123123',
            'position': constants.ROLES.ACCOUNTING_MANAGER
        })
        self.request.user = self.employee.account
        self.add_session()
        response: HttpResponse = views.addEmployeePage(self.request)
        response.client = Client()
        emp: Employee | None = None
        try:
            emp = Employee.objects.get(person__name='Test123')
        except Employee.DoesNotExist:
            pass
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(
            self.hr_pages + constants.PAGES.EMPLOYEES_PAGE),
            target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertIsNotNone(emp)
        self.assertEquals(emp.person.contacting_email, 'test@test.te')
        self.assertEquals(emp.account.username, 'Test123')
        self.assertEquals(emp.account.groups.first().name,
                          constants.ROLES.ACCOUNTING_MANAGER)

    def test_employee_record_page(self) -> None:
        emp: Employee = Employee.objects.create(
            person=Person.objects.create(name='TEST EMPLOYEE RECORD PAGE'),
            position=constants.ROLES.WAREHOUSE_ADMIN
        )

        response: HttpResponse = views.employeePage(self.request, emp.id)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

        response: HttpResponse = views.employeePage(
            self.request, self.employee.id)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

        response: HttpResponse = views.employeePage(
            self.request, Employee.objects.get(position=constants.ROLES.CEO).id)
        response.client = Client()
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(
            constants.PAGES.UNAUTHORIZED_PAGE),
            target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)

        self.request.user = User.objects.first()
        self.assertEquals(self.request.user.groups.first().name,
                          constants.ROLES.CEO)
        response: HttpResponse = views.employeePage(
            self.request, Employee.objects.get(position=constants.ROLES.CEO).id)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

        response: HttpResponse = views.employeePage(
            self.request, self.employee.id)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

    def test_update_employee_record(self) -> None:
        response: HttpResponse = views.updateEmployeePage(
            self.request, 1)  # CEO page viewed by HR
        response.client = Client()
        self.assertEquals(self.request.user.groups.first().name,
                          constants.ROLES.HUMAN_RESOURCES)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(
            constants.PAGES.UNAUTHORIZED_PAGE),
            target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)

        response: HttpResponse = views.updateEmployeePage(
            self.request, self.employee.id)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

        emp: Employee = Employee.create(
            self.employee.person.name,
            person=Person.create(self.employee.person.name, name="TEST"),
            position=constants.ROLES.WAREHOUSE_ADMIN
        )
        self.request = self.client.post('/', {
            'name': 'TEST UPDATE',
            'gender': constants.GENDER.MALE,
            'nationality': constants.COUNTRY.get('YEMEN'),
            'date_of_birth': timezone.datetime(year=1999, month=12, day=12).date(),
            'contacting_email': 'test@test.te',
            'phone_number': '+123 123123123',
            'position': constants.ROLES.WAREHOUSE_ADMIN
        })
        self.request.user = self.employee.account
        self.add_session()
        response: HttpResponse = views.updateEmployeePage(
            self.request, emp.id)
        response.client = Client()
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(
            self.hr_pages + constants.PAGES.EMPLOYEE_RECORD_PAGE, args=[emp.id]),
            target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertEquals(Employee.objects.get(
            id=emp.id).person.name, 'TEST UPDATE')

        self.request = self.client.get('/')
        self.request.user = User.objects.get(username='CEO')
        response: HttpResponse = views.updateEmployeePage(
            self.request, 1)  # CEO page viewed by CEO
        self.assertEquals(self.request.user.groups.first().name,
                          constants.ROLES.CEO)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

    def test_delete_employee(self) -> None:
        response: HttpResponse = views.deleteEmployeePage(
            self.request, 1)  # CEO delete page viewed by HR
        response.client = Client()
        self.assertEquals(self.request.user.groups.first().name,
                          constants.ROLES.HUMAN_RESOURCES)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(constants.PAGES.UNAUTHORIZED_PAGE),
                             target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)

        self.request: HttpRequest = self.client.delete('/')
        self.request.user = self.employee.account
        self.add_session()
        response: HttpResponse = views.deleteEmployeePage(self.request, 1)
        response.client = Client()
        emp: Employee | None = None
        try:
            emp = Employee.objects.get(id=1)
        except Employee.DoesNotExist:
            pass
        self.assertIsNotNone(emp)
        self.assertEquals(emp.position, constants.ROLES.CEO)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(constants.PAGES.UNAUTHORIZED_PAGE),
                             target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)

        emp: Employee = Employee.objects.create(
            person=Person.objects.create(name='Test Delete Employee'),
            position=constants.ROLES.ACCOUNTING_MANAGER
        )
        emp_id: int = emp.id
        response: HttpResponse = views.deleteEmployeePage(self.request, emp.id)
        response.client = Client()
        emp: Employee | None = None
        try:
            emp = Employee.objects.get(id=emp_id)
        except Employee.DoesNotExist:
            pass
        self.assertIsNone(emp)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(self.hr_pages + constants.PAGES.EMPLOYEES_PAGE),
                             target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)

    def test_distributors_page(self) -> None:
        response: HttpResponse = views.distributorsPage(self.request)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

    def test_add_distributors_page(self) -> None:
        response: HttpResponse = views.addDistributorPage(self.request)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

        self.request = self.client.post('/', {
            'name': 'TeSt add new distributor',
            'gender': constants.GENDER.MALE,
            'nationality': constants.COUNTRY.get('YEMEN'),
            'date_of_birth': timezone.datetime(year=1999, month=12, day=12).date(),
            'contacting_email': 'test@test.te',
            'phone_number': '+123 123123123',
        })
        self.request.user = self.employee.account
        self.add_session()
        response: HttpResponse = views.addDistributorPage(self.request)
        response.client = Client()
        distributor: Distributor | None = None
        try:
            distributor = Distributor.objects.get(
                person__name='TeSt add new distributor')
        except Employee.DoesNotExist:
            pass
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(
            self.hr_pages + constants.PAGES.DISTRIBUTORS_PAGE),
            target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertIsNotNone(distributor)
        self.assertEquals(distributor.person.contacting_email, 'test@test.te')
        self.assertEquals(distributor.account.username, 'TeSt')
        self.assertEquals(distributor.account.groups.first().name,
                          constants.ROLES.DISTRIBUTOR)

    def test_distributor_record_page(self) -> None:
        distributor: Distributor = Distributor.objects.create(
            person=Person.objects.create(name='TEST DISTRIBUTOR RECORD PAGE'),
        )

        response: HttpResponse = views.distributorPage(
            self.request, distributor.id)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

    def test_update_distributors_page(self) -> None:
        distributor: Distributor = Distributor.create(
            self.request,
            person=Person.create(self.request, name='Test Update Distributor'),
        )

        response: HttpResponse = views.updateDistributorPage(
            self.request, distributor.id)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

        self.request = self.client.post('/', {
            'name': 'tEsT Update distributor',
            'gender': constants.GENDER.MALE,
            'nationality': constants.COUNTRY.get('YEMEN'),
            'date_of_birth': timezone.datetime(year=1999, month=12, day=12).date(),
            'contacting_email': 'test@test.te',
            'phone_number': '+123 123123123',
        })
        self.request.user = self.employee.account
        self.add_session()
        response: HttpResponse = views.updateDistributorPage(
            self.request, distributor.id)
        response.client = Client()
        distributor: Distributor = Distributor.objects.get(id=distributor.id)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(
            self.hr_pages + constants.PAGES.DISTRIBUTOR_RECORD_PAGE, args=[distributor.id]),
            target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertEquals(distributor.person.name, 'tEsT Update distributor')
        self.assertEquals(distributor.person.contacting_email, 'test@test.te')
        self.assertEquals(distributor.account.username, 'Test')
        self.assertEquals(distributor.account.groups.first().name,
                          constants.ROLES.DISTRIBUTOR)

    def test_delete_employee(self) -> None:
        distributor: Distributor = Distributor.create(
            self.request,
            person=Person.create(self.request, name='Test Delete Distributor'),
        )

        self.request = self.client.delete('/')
        self.request.user = self.employee.account
        self.add_session()
        dis_id: int = distributor.id
        response: HttpResponse = views.deleteDistributorPage(
            self.request, dis_id)
        response.client = Client()
        distributor: Distributor | None = None
        try:
            distributor = Distributor.objects.get(id=dis_id)
        except Distributor.DoesNotExist:
            pass
        self.assertIsNone(distributor)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(self.hr_pages + constants.PAGES.DISTRIBUTORS_PAGE),
                             target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)

    def test_employees_tasks_page(self) -> None:
        response: HttpResponse = views.employeeTasksPage(self.request)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

    def test_add_task_page(self) -> None:
        response: HttpResponse = views.addTaskPage(self.request)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

        self.request = self.client.post('/', {
            'employee': self.employee.id,
            'task': 'task to HR by HR',
            'description': 'This must be invalid'
        })
        self.request.user = self.employee.account
        self.add_session()
        response: HttpResponse = views.addTaskPage(self.request)
        self.assertEquals(Task.objects.count(), 0)

        self.request = self.client.post('/', {
            'employee': Employee.objects.create(
                person=Person.objects.create(name='Test!@#'),
                position=constants.ROLES.ACCOUNTING_MANAGER
            ).id,
            'task': 'task to AM by HR',
            'description': 'This must be valid'
        })
        self.request.user = self.employee.account
        self.add_session()
        response: HttpResponse = views.addTaskPage(self.request)
        self.assertEquals(Task.objects.filter(
            employee__person__name='Test!@#').count(), 1)

        self.request = self.client.post('/', {
            'employee': self.employee.id,
            'task': 'task to HR by CEO',
            'description': 'This must be valid'
        })
        self.request.user = User.objects.get(username='CEO')
        self.add_session()
        self.assertEquals(self.request.user.is_authenticated, True)
        self.assertEquals(
            self.request.user.groups.first().name, constants.ROLES.CEO)
        response: HttpResponse = views.addTaskPage(self.request)
        self.assertEquals(Task.objects.count(), 2)
        task: Task = Task.objects.last()
        self.assertEquals(task.employee, self.employee)

    def test_detail_task_page(self) -> None:
        task: Task = Task.objects.create(
            employee=Employee.objects.create(
                person=Person.objects.create(name='Test!@#'),
                position=constants.ROLES.ACCOUNTING_MANAGER
            ),
            task='Test',
            description='Test detail task page'
        )
        response: HttpResponse = views.taskPage(self.request, task.id)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

        task: Task = Task.objects.create(
            employee=self.employee,
            task='Test',
            description='Test access HR task by HR'
        )
        response: HttpResponse = views.taskPage(self.request, task.id)
        response.client = Client()
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(constants.PAGES.UNAUTHORIZED_PAGE),
                             target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)

        self.request.user = User.objects.get(username='CEO')
        self.add_session()
        response: HttpResponse = views.taskPage(self.request, task.id)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

    def test_update_task(self) -> None:
        task: Task = Task.objects.create(
            employee=self.employee,
            task='Test',
            description='Test access HR task by HR'
        )
        response: HttpResponse = views.updateTaskPage(self.request, task.id)
        response.client = Client()
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(
            constants.PAGES.UNAUTHORIZED_PAGE),
            target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)

        emp: Employee = Employee.create(
            self.request,
            person=Person.objects.create(name='Test123'),
            position=constants.ROLES.ACCOUNTING_MANAGER

        )
        task: Task = Task.create(
            self.request,
            employee=emp,
            task='Test',
            description='Test update task page'
        )
        self.request = self.client.post('/', {
            'employee': emp.id,
            'task': 'Test',
            'description': 'Test updated'
        })
        self.request.user = self.employee.account
        self.add_session()
        response: HttpResponse = views.updateTaskPage(self.request, task.id)
        response.client = Client()
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(self.hr_pages + constants.PAGES.DETAILED_TASK_PAGE,
                             args=[task.id]), target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertEquals(Task.objects.get(
            id=task.id).description, 'Test updated')

    def test_delete_employee_task(self) -> None:
        task: Task = Task.objects.create(
            employee=self.employee,
            task='Test',
            description='Test delete HR task by HR'
        )
        response: HttpResponse = views.deleteTaskPage(self.request, task.id)
        response.client = Client()
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(
            constants.PAGES.UNAUTHORIZED_PAGE),
            target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)

        emp: Employee = Employee.create(
            self.request,
            person=Person.objects.create(name='Test123'),
            position=constants.ROLES.ACCOUNTING_MANAGER

        )
        task: Task = Task.create(
            self.request,
            employee=emp,
            task='Test',
            description='Test delete task page'
        )
        self.request = self.client.delete('/')
        self.request.user = self.employee.account
        self.add_session()
        self.assertEquals(Task.objects.filter(employee=emp).count(), 1)
        response: HttpResponse = views.deleteTaskPage(self.request, task.id)
        response.client = Client()
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertRedirects(response, reverse(self.hr_pages + constants.PAGES.EMPLOYEES_TASKS_PAGE),
                             target_status_code=constants.RESPONSE_STATUS_CODE.REDIRECT)
        self.assertEquals(Task.objects.filter(employee=emp).count(), 0)

    def test_evaluation_page(self) -> None:
        response: HttpResponse = views.evaluationPage(self.request)
        self.assertEquals(response.status_code,
                          constants.RESPONSE_STATUS_CODE.SUCCESS)

    def test_weekly_evaluation_page(self) -> None: pass

    def test_employees_task_evaluation_page(self) -> None: pass
