import logging
from logging import Logger

from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils import timezone

from main import constants
from main.parameters import getParameterValue

from .models import Week, Task, Employee

logger: Logger = logging.getLogger(constants.LOGGERS.MAIN)


def addWeekToRate():
    """
    Add a new week to rate every Sunday
    """
    logger.info(
        '=========== CRON STARTED TO ADD NEW WEEK TO RATE EMPLOYEES ===========')
    last_week: Week = Week.getLastInsertedObject()
    if last_week is None or last_week.week_end_date + timezone.timedelta(days=6) < timezone.now().date():
        try:
            emp = Employee.get(
                position=constants.ROLES.HUMAN_RESOURCES)
        except Employee.DoesNotExist:
            logger.info("Cron failed to add week to rate for HR, "
                        + "there is no HR role added in the employee list.")
            return
        Week.create(
            constants.SYSTEM_CRON_NAME,
            week_start_date=timezone.now() - timezone.timedelta(days=6),
            week_end_date=timezone.now().date()
        )
        deadline_days: int = getParameterValue(
            constants.PARAMETERS.WEEKLY_RATE_TASK_PERIOD)
        Task.create(
            constants.SYSTEM_CRON_NAME,
            employee=emp,
            task=getParameterValue(
                constants.PARAMETERS.WEEKLY_RATE_TASK_NAME),
            description=getParameterValue(
                constants.PARAMETERS.WEEKLY_RATE_TASK_DESCRIPTION),
            deadline_date=None if not deadline_days else timezone.now() +
            timezone.timedelta(days=deadline_days)
        )
        logger.info("Corn added new week to rate successfully.")
    else:
        logger.warning("Corn setting not will, week to rate dose not added.")
    logger.info(
        '=========== CRON FINISHED ADDING NEW WEEK TO RATE EMPLOYEES ===========')


def checkTasksStatus():
    """
    Check if the  task is overdue and change it status in database
    """
    logger.info('=========== CRON STARTED TO CHECK TASKS STATUS ===========')
    Tasks: QuerySet[Task] = Task.filter(
        Q(status=constants.TASK_STATUS.IN_PROGRESS) |
        Q(status=constants.TASK_STATUS.OVERDUE),
        created__range=(timezone.now() - timezone.timedelta(days=31),
                        timezone.now()))
    for task in Tasks:
        if task.status == constants.TASK_STATUS.IN_PROGRESS:
            if task.time_left == 'Overdue':
                task.setStatus(constants.SYSTEM_CRON_NAME,
                               constants.TASK_STATUS.OVERDUE)
                logger.info(f"The task [{task.id}] status "
                            + f"changed to {task.status}.")
        elif task.status == constants.TASK_STATUS.OVERDUE:
            if task.time_left != 'Overdue':
                task.setStatus(constants.SYSTEM_CRON_NAME,
                               constants.TASK_STATUS.IN_PROGRESS)
                logger.info(f"The task [{task.id}] status "
                            + f"changed to {task.status}.")
    logger.info('=========== CRON FINISHED CHECKING TASKS STATUS ===========')
