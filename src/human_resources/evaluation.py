from django.db.models import Q
from django.db.models.functions import Lower
from main import constant
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
    if not WeeklyRate.objects.filter(employee=emp_id).exists():
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
        rate, count = 0, 0
        # Get all weekly rates of the employee
        emp_weekly_rates = WeeklyRate.objects.filter(
            employee=emp_id).order_by('-id')
        for i in emp_weekly_rates:
            # Check if 4 weeks already calculated then break if it is.
            if count == 4:
                break
            rate += i.rate
            count += 1

        # Check to avoid ZeroDivisionError
        return 0 if count == 0 else round((rate/count), 2)

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
    from django.utils import timezone
    from datetime import timedelta

    rate, count = 0, 0
    today = timezone.now()
    # The date of the day before the specified days form today
    end_date = today - timedelta(days=days)
    # Get all employee's tasks last specified days
    empTasks = Task.objects.filter(employee=emp_id,
                                   receiving_date__range=[end_date, today])
    if empTasks.exists():
        for task in empTasks:
            # Get the task rate of the task
            task_rate = TaskRate.objects.filter(task=task)
            if task_rate.exists():
                task_rate = task_rate[0]
                rate += task_rate.rate
                rate += task_rate.on_time_rate
                count += 1
        # Check to avoid ZeroDivisionError
        if count != 0:
            return round(((rate/count) / 2), 2)

    return 0


def monthlyTaskRate(emp_id: int) -> float:
    """
    This function will return the monthly task rate of the employee 
    by calculating the last 30 day's task rates, 

    Args:
        emp_id (int): Employee ID

    Returns:
        float: Monthly task rate
    """
    return getTaskRateFrom(emp_id, 30)


def weeklyRate(week_id: int, emp_id: int) -> float:
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
        # Check if there is a last week rate for the employee
        if week_id != -1:
            return WeeklyRate.objects.get(week__id=week_id, employee=emp_id).rate

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
    # All Time Weekly Rate
    rate, count = 0, 0
    # Get all employee's weekly rats
    emp_weekly_rates = WeeklyRate.objects.filter(employee=emp_id)
    if emp_weekly_rates.exists():
        for weekly_rate in emp_weekly_rates:
            rate += weekly_rate.rate
            count += 1
    # Check to avoid ZeroDivisionError
    all_time_weekly_rate = 0 if count == 0 else rate/count
    del rate, count

    # All Tasks Rate
    rate, count = 0, 0
    empTasks = Task.objects.filter(employee=emp_id)
    if empTasks.exists():
        for task in empTasks:
            # Get all employee's task rats
            task_rate = TaskRate.objects.filter(task=task)
            if task_rate.exists():
                task_rate = task_rate[0]
                rate += task_rate.rate
                rate += task_rate.on_time_rate
                count += 1
    # Check to avoid ZeroDivisionError
    all_task_rate = 0 if count == 0 else (rate/count) / 2

    if not all_time_weekly_rate:
        return round(all_task_rate, 2)
    elif not all_task_rate:
        return round(all_time_weekly_rate, 2)
    else:
        # Check to avoid ZeroDivisionError
        try:
            return round(((all_time_weekly_rate + all_task_rate) / 2), 2)
        except ZeroDivisionError:
            return 0


def getEvaluation(emp_id=-1) -> dict:
    """
    This function if employee id not specified it will return all employees' evaluations 
    else it will return the evaluation of the specified employee's evaluations

    Args:
        emp_id (int, optional): Employee ID. Defaults to -1.

    Returns:
        dict: Employee/s evaluation
    """
    evaluation = {}
    # if the employee specified
    if emp_id != -1:
        employee = Employee.objects.get(id=emp_id)
        evaluation = {'Employee': employee,
                      'MonthlyRate': monthlyRate(emp_id),
                      'WeeklyRate': weeklyRate(Week.getLastWeekID(), emp_id),
                      'MonthlyTaskRate': monthlyTaskRate(emp_id),
                      'MonthlyOverallEvaluation': monthlyOverallEvaluation(emp_id),
                      'AllTimeEvaluation': allTimeEvaluation(emp_id),
                      }
    # if the employee not specified
    else:
        for employee in Employee.objects.filter(~Q(position=constant.ROLES.CEO)).order_by(Lower('person__name')):
            emp_id = employee.id
            evaluation[employee.person.name] = {'Employee': employee,
                                                'MonthlyRate': monthlyRate(emp_id),
                                                'WeeklyRate': weeklyRate(Week.getLastWeekID(), emp_id),
                                                'MonthlyTaskRate': monthlyTaskRate(emp_id),
                                                'MonthlyOverallEvaluation': monthlyOverallEvaluation(emp_id),
                                                'AllTimeEvaluation': allTimeEvaluation(emp_id)
                                                }

    return evaluation


def allEmployeesWeeklyEvaluations():
    rate, count = 0, 0
    # Get all employees except the CEO
    employees = Employee.objects.filter(~Q(position=constant.ROLES.CEO))
    for employee in employees:
        # Get all employees weekly rates
        emp_weekly_rate = weeklyRate(Week.getLastWeekID(), employee.id)
        if emp_weekly_rate:
            rate += emp_weekly_rate
            count += 1
    # Check to avoid ZeroDivisionError
    try:
        return round(rate/count, 2)
    except ZeroDivisionError:
        return 0


def allEmployeesMonthlyEvaluations():
    rate, count = 0, 0
    # Get all employees except the CEO
    employees = Employee.objects.filter(~Q(position=constant.ROLES.CEO))
    for employee in employees:
        # Get all employees monthly rates
        emp_monthly_rate = monthlyRate(employee.id)
        if emp_monthly_rate:
            rate += emp_monthly_rate
            count += 1
    # Check to avoid ZeroDivisionError
    try:
        return round(rate/count, 2)
    except ZeroDivisionError:
        return 0


def allEmployeesMonthlyTaskRate():
    rate, count = 0, 0
    # Get all employees except the CEO
    employees = Employee.objects.filter(~Q(position=constant.ROLES.CEO))
    for employee in employees:
        # Get all employees monthly task rates
        emp_monthly_rate = monthlyTaskRate(employee.id)
        if emp_monthly_rate:
            rate += emp_monthly_rate
            count += 1
    # Check to avoid ZeroDivisionError
    try:
        return round(rate/count, 2)
    except ZeroDivisionError:
        return 0


def allEmployeesMonthlyOverallEvaluation():
    rate, count = 0, 0
    # Get all employees except the CEO
    employees = Employee.objects.filter(~Q(position=constant.ROLES.CEO))
    for employee in employees:
        # Get all employees monthly overall rates
        emp_monthly_rate = monthlyOverallEvaluation(employee.id)
        if emp_monthly_rate:
            rate += emp_monthly_rate
            count += 1
    # Check to avoid ZeroDivisionError
    try:
        return round(rate/count, 2)
    except ZeroDivisionError:
        return 0
