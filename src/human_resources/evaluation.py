from typing import Optional

from django.db.models import Q
from django.db.models.functions import Lower
from django.db.models.query import QuerySet
from django.utils import timezone

from main import constants

from .models import Employee, Task, TaskRate, Week, WeeklyRate


def _newEmployee(emp_id: int) -> bool:
    """
    This function checks if the Employee is new 
    by checking if there is any weekly rate existed
    it will return False if there are any rates found

    Args:
        emp_id (int): Employee ID

    Returns:
        bool: True if the employee is new else False
    """
    if not WeeklyRate.isExists(employee=emp_id):
        return True
    return False


def monthlyRate(emp_id: int) -> float:
    """
    This function will return the monthly rate of the employee 
    by calculating the last 4 weeks' rates, 
    if the employee has not been weekly rated the function will return 0

    Args:
        emp_id (int): Employee ID

    Returns:
        float: Monthly rate
    """
    if not _newEmployee(emp_id):
        WEEKS_IN_A_MONTH = 4
        rate: float = 0
        count: int = 0
        month_period: tuple[timezone.datetime, ...] = (
            timezone.now() - timezone.timedelta(days=30), timezone.now())
        emp_weekly_rates: QuerySet[WeeklyRate] = WeeklyRate.orderFiltered(
            'id', reverse=True, employee=emp_id, created__range=month_period)
        for i in emp_weekly_rates:
            if count == WEEKS_IN_A_MONTH:
                break
            rate += i.rate
            count += 1

        return 0 if count == 0 else round((rate / count), 2)

    return 0


def getTaskRateFrom(emp_id: int, days: int) -> float:
    """
    This function returns the tasks rate of the employee 
    from last the specified days the currant day
    if the employee has no tasks or his tasks is not rated 
    the function will return 0

    Args:
        emp_id (int): Employee ID

    Returns:
        float: Monthly task rate
    """
    rate: float = 0
    count: int = 0
    period: tuple[timezone.datetime, ...] = (
        timezone.now() - timezone.timedelta(days=days), timezone.now())
    empTasks: QuerySet[Task] = Task.filter(
        employee=emp_id, created__range=period)
    # if empTasks.exists():
    for task in empTasks:
        try:
            task_rate: TaskRate = TaskRate.get(task=task,
                                               created__range=period)
            if not task_rate:
                continue
            rate += task_rate.rate
            rate += task_rate.on_time_rate
            count += 1
        except TaskRate.DoesNotExist:
            pass
    if count != 0:
        return round(((rate / count) / 2), 2)

    return 0


def monthlyTaskRate(emp_id: int) -> float:
    """
    Calculating the last 30 day's task rates, 

    Args:
        emp_id (int): Employee ID

    Returns:
        float: Monthly task rate
    """
    return getTaskRateFrom(emp_id, 30)


def weeklyRate(emp_id: int) -> float:
    """
    This function will return the last week rate of the employee 
    if the employee has not been weekly rated ever the function will return 0

    Args:
        last_week_id (int): ID of the las week
        emp_id (int): Employee ID

    Returns:
        float: Employee weekly rate
    """
    if not _newEmployee(emp_id):
        last_week: Week = Week.orderFiltered("created").last()
        weekly_rate: WeeklyRate = WeeklyRate.get(
            week=last_week, employee=emp_id)
        if weekly_rate:
            return weekly_rate.rate
    return 0


def monthlyOverallEvaluation(emp_id: int) -> float:
    """
    This function calculating the monthly overall evaluation

    Args:
        em_id (int): Employee ID

    Returns:
        float: Monthly overall evaluation
    """
    if not _newEmployee(emp_id):
        return round(((monthlyRate(emp_id) + monthlyTaskRate(emp_id)) / 2), 2)
    else:
        return monthlyTaskRate(emp_id)


def allTimeEvaluation(emp_id: int) -> float:
    """
    This function calculating all time evaluation for the employee
    Args:
        emp_id (int): Employee ID

    Returns:
        float: All time evaluation
    """
    rate: float = 0
    count: int = 0
    emp_weekly_rates: QuerySet[WeeklyRate] = WeeklyRate.filter(employee=emp_id)
    if emp_weekly_rates.exists():
        for weekly_rate in emp_weekly_rates:
            rate += weekly_rate.rate
            count += 1
    all_time_weekly_rate: float = 0 if count == 0 else rate / count
    del rate, count

    # All Tasks Rate
    rate: float = 0
    count: int = 0
    empTasks: QuerySet[Task] = Task.filter(employee=emp_id)
    if empTasks.exists():
        for task in empTasks:
            try:
                task_rate: TaskRate = TaskRate.get(task=task)
                rate += task_rate.rate
                rate += task_rate.on_time_rate
                count += 1
            except TaskRate.DoesNotExist:
                pass
    all_task_rate: float = 0 if count == 0 else (rate / count) / 2

    if not all_time_weekly_rate:
        return round(all_task_rate, 2)
    elif not all_task_rate:
        return round(all_time_weekly_rate, 2)
    else:
        try:
            return round(((all_time_weekly_rate + all_task_rate) / 2), 2)
        except ZeroDivisionError:
            return 0


def getEvaluation(emp_id: Optional[int] = -1) -> dict[str, float | Employee]:
    """
    This function if employee id not specified it will return all employees' evaluations 
    else it will return the evaluation of the specified employee's evaluations

    Args:
        emp_id (int, optional): Employee ID. Defaults to -1.

    Returns:
        dict: Employee/s evaluation
    """
    evaluation: dict = {}
    # if the employee specified
    if emp_id != -1:
        employee: Employee = Employee.get(id=emp_id)
        evaluation = {'Employee': employee,
                      'MonthlyRate': monthlyRate(emp_id),
                      'WeeklyRate': weeklyRate(emp_id),
                      'MonthlyTaskRate': monthlyTaskRate(emp_id),
                      'MonthlyOverallEvaluation': monthlyOverallEvaluation(emp_id),
                      'AllTimeEvaluation': allTimeEvaluation(emp_id),
                      }
    # if the employee not specified
    else:
        for employee in Employee.orderFiltered(Lower('person__name'), ~Q(position=constants.ROLES.CEO)):
            emp_id: int = employee.id
            evaluation[employee.person.name] = {'Employee': employee,
                                                'MonthlyRate': monthlyRate(emp_id),
                                                'WeeklyRate': weeklyRate(emp_id),
                                                'MonthlyTaskRate': monthlyTaskRate(emp_id),
                                                'MonthlyOverallEvaluation': monthlyOverallEvaluation(emp_id),
                                                'AllTimeEvaluation': allTimeEvaluation(emp_id)
                                                }

    return evaluation


def allEmployeesWeeklyEvaluations() -> float:
    rate: float = 0
    count: int = 0
    employees: QuerySet[Employee] = Employee.filter(
        ~Q(position=constants.ROLES.CEO))
    for employee in employees:
        emp_weekly_rate: float = weeklyRate(employee.id)
        if emp_weekly_rate:
            rate += emp_weekly_rate
            count += 1
    try:
        return round(rate / count, 2)
    except ZeroDivisionError:
        return 0


def allEmployeesMonthlyEvaluations() -> float:
    rate: float = 0
    count: int = 0
    employees: QuerySet[Employee] = Employee.filter(
        ~Q(position=constants.ROLES.CEO))
    for employee in employees:
        emp_monthly_rate: float = monthlyRate(employee.id)
        if emp_monthly_rate:
            rate += emp_monthly_rate
            count += 1
    try:
        return round(rate / count, 2)
    except ZeroDivisionError:
        return 0


def allEmployeesMonthlyTaskRate() -> float:
    rate: float = 0
    count: int = 0
    employees: QuerySet[Employee] = Employee.filter(
        ~Q(position=constants.ROLES.CEO))
    for employee in employees:
        emp_monthly_rate: float = monthlyTaskRate(employee.id)
        if emp_monthly_rate:
            rate += emp_monthly_rate
            count += 1
    try:
        return round(rate / count, 2)
    except ZeroDivisionError:
        return 0


def allEmployeesMonthlyOverallEvaluation() -> float:
    rate: float = 0
    count: int = 0
    employees: QuerySet[Employee] = Employee.objects.filter(
        ~Q(position=constants.ROLES.CEO))
    for employee in employees:
        emp_monthly_rate: float = monthlyOverallEvaluation(employee.id)
        if emp_monthly_rate:
            rate += emp_monthly_rate
            count += 1
    try:
        return round(rate / count, 2)
    except ZeroDivisionError:
        return 0
