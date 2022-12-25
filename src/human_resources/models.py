from typing import Union

from django.contrib.auth.models import User
from django.db import models
from django.http import HttpRequest
from django.utils import timezone

from main.models import BaseModel, Person
from main import constants


class Employee(BaseModel):

    person: Person = models.OneToOneField(Person, on_delete=models.SET_NULL,
                                          null=True, blank=True)
    account: User = models.OneToOneField(User, on_delete=models.SET_NULL,
                                         null=True, blank=True)
    position: str = models.CharField(max_length=20,
                                     choices=constants.CHOICES.POSITIONS)

    def __str__(self) -> str:
        return self.person.name

    def setPerson(self, requester: Union[HttpRequest, str], person: Person) -> None:
        self.person = person
        self.setCreatedByUpdatedBy(requester)

    def setAccount(self, requester: Union[HttpRequest, str], account: User) -> None:
        self.account = account
        self.setCreatedByUpdatedBy(requester)

    def setPosition(self, requester: Union[HttpRequest, str], position: str) -> None:
        self.position = position
        self.setCreatedByUpdatedBy(requester)


class Task(BaseModel):

    employee: Employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task: str = models.CharField(max_length=30)
    description: str = models.TextField(max_length=500, default="-")
    status: str = models.CharField(max_length=20, choices=constants.CHOICES.TASK_STATUS,
                                   default=constants.TASK_STATUS.IN_PROGRESS)
    deadline_date: timezone.datetime = models.DateTimeField(null=True,
                                                            blank=True)
    submission_date: timezone.datetime = models.DateTimeField(null=True,
                                                              blank=True)
    is_rated: bool = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.task

    @property
    def receiving_date(self) -> str:
        return self.created

    @property
    def time_left(self) -> str:
        """
        Calculating the time difference between the time now and the task's deadline.

        Returns:
            str: The time left from the task deadline.
        """
        # If the deadline date is declared
        if not self.submission_date:
            if self.deadline_date:
                time_difference: str = str(self.deadline_date - timezone.now())
                # Check if the time difference is a negative value or 0:00:00
                if time_difference.startswith('-') or time_difference.startswith("0:00:00"):
                    return 'Overdue'
                else:
                    return time_difference[:-7] if len(time_difference.split(":")[-1]) > 6 else time_difference
            else:
                return "Open"
        else:
            return "Submitted"

    def setEmployee(self, requester: Union[HttpRequest, str], employee: Employee) -> None:
        self.employee = employee
        self.setCreatedByUpdatedBy(requester)

    def setName(self, requester: Union[HttpRequest, str], name: str) -> None:
        self.name = name
        self.setCreatedByUpdatedBy(requester)

    def setDescription(self, requester: Union[HttpRequest, str], description: str) -> None:
        self.description = description
        self.setCreatedByUpdatedBy(requester)

    def setStatus(self, requester: Union[HttpRequest, str], status: str) -> None:
        self.status = status
        self.setCreatedByUpdatedBy(requester)

    def setDeadlineDate(self, requester: Union[HttpRequest, str], deadline_date: timezone.datetime) -> None:
        self.deadline_date = deadline_date
        self.setCreatedByUpdatedBy(requester)

    def setSubmissionDate(self, requester: Union[HttpRequest, str], submission_date: timezone.datetime) -> None:
        self.submission_date = submission_date
        self.setCreatedByUpdatedBy(requester)

    def setRated(self, requester: Union[HttpRequest, str], is_rated: bool) -> None:
        self.is_rated = is_rated
        self.setCreatedByUpdatedBy(requester)


class TaskRate(BaseModel):

    task: Task = models.OneToOneField(Task, on_delete=models.CASCADE)
    on_time_rate: float = models.FloatField()
    rate: float = models.FloatField()

    def __str__(self) -> str:
        return str(self.rate)

    def setTask(self, requester: Union[HttpRequest, str], task: Task) -> None:
        self.task = task
        self.setCreatedByUpdatedBy(requester)

    def setOnTimeRate(self, requester: Union[HttpRequest, str], on_time_rate: float) -> None:
        self.on_time_rate = on_time_rate
        self.setCreatedByUpdatedBy(requester)

    def setRate(self, requester: Union[HttpRequest, str], rate: float) -> None:
        self.rate = rate
        self.setCreatedByUpdatedBy(requester)


class Week(BaseModel):

    week_start_date: timezone.datetime = models.DateField()
    week_end_date: timezone.datetime = models.DateField()
    is_rated: bool = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.week_start_date}'

    def setWeekStartDate(self, requester: Union[HttpRequest, str], week_start_date: timezone.datetime) -> None:
        self.week_start_date = timezone.datetime.date(week_start_date)
        self.setCreatedByUpdatedBy(requester)

    def setWeekEndDate(self, requester: Union[HttpRequest, str], week_end_date: timezone.datetime) -> None:
        self.week_end_date = timezone.datetime.date(week_end_date)
        self.setCreatedByUpdatedBy(requester)

    def setRated(self, requester: Union[HttpRequest, str], is_rated: bool) -> None:
        self.is_rated = is_rated
        self.setCreatedByUpdatedBy(requester)


class WeeklyRate(BaseModel):

    week: Week = models.ForeignKey(Week, on_delete=models.CASCADE)
    employee: Employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    rate: float = models.FloatField()

    def __str__(self) -> str:
        return f"{str(self.week)} - {self.employee.person.name}"

    def setWeek(self, requester: Union[HttpRequest, str], week: Week) -> None:
        self.week = week
        self.setCreatedByUpdatedBy(requester)

    def setEmployee(self, requester: Union[HttpRequest, str], employee: Employee) -> None:
        self.employee = employee
        self.setCreatedByUpdatedBy(requester)

    def setRate(self, requester: Union[HttpRequest, str], rate: float) -> None:
        self.rate = rate
        self.setCreatedByUpdatedBy(requester)
