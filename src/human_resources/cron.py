from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Week, Task, Employee


def addWeekToRate():
    """
    Add a new week to rate every Sunday
    """
    # Now is the date and time. Today only the date of today
    now = timezone.now()
    today = datetime.strftime(timezone.now(), '%Y-%m-%d')
    # Check if the last week object is today
    last_week: Week = Week.getLastInsertedObject()
    if str(last_week.week_end_date) != today:
        emp = Employee.objects.get(position='Human Resources')
        # If it's not today add new week object
        Week.objects.create(
            week_start_date=now - timedelta(days=6),
            week_end_date=today
        )
        # Add auto task to HR for evaluating employees
        Task.objects.create(
            employee=emp,
            name="Evaluate employees",
            description="Make sure to rate each employee on their weekly evaluations.",
            deadline_date=now + timedelta(days=7)
        )


def checkTaskDateTime():
    """
    Check if the  task is overdue and change it status in database
    """
    # Get all unsubmitted task
    Tasks = Task.objects.filter(
        ~Q(status="Late-Submission") & ~Q(status="On-Time"))
    now = datetime.strftime(timezone.now(), '%Y-%m-%d %H:%M:%s')

    for task in Tasks:
        # Check if the task past the deadline
        if task.status == "In-Progress":
            if str(task.deadline_date) <= now:
                task.status = "Overdue"
                task.save()
        # Check the task in 'Overdue' state if the deadline updated
        elif task.status == "Overdue":
            if str(task.deadline_date) >= now:
                task.status = "In-Progress"
                task.save()
