from django.db import models
from django.contrib.auth.models import User
from main.models import Person


class Employee(models.Model):

    POSITIONS = [
        ('CEO', 'CEO'),
        ('Human Resources', 'Human Resources'),
        ('Warehouse Admin', 'Warehouse Admin'),
        ('Accounting Manager', 'Accounting Manager'),
        ('Social Media Manager', 'Social Media Manager'),
        ('Designer', 'Designer'),
        ('Distributor', 'Distributor')
    ]

    id = models.AutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.SET_NULL,
                                  null=True, blank=True)
    account = models.OneToOneField(User, on_delete=models.SET_NULL,
                                   null=True, blank=True)
    position = models.CharField(max_length=20, choices=POSITIONS)

    def __str__(self) -> str:
        return self.person.name


class Task(models.Model):

    STATUS = [
        ('In-Progress', 'In-Progress'),
        ('On-Time', 'On-Time'),
        ('Late-Submission', 'Late-Submission'),
        ('Overdue', 'Overdue')
    ]

    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL,
                                 null=True, blank=True)
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=500, default="-",
                                   null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, null=True,
                              blank=True, default='In-Progress')
    receiving_date = models.DateTimeField(auto_now_add=True)
    deadline_date = models.DateTimeField(null=True, blank=True)
    submission_date = models.DateTimeField(null=True, blank=True)
    is_rated = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    @property
    def getTimeLeft(self) -> str:
        """
        Calculating the time difference between the time now and the task's deadline.

        Returns:
            str: The time left from the task deadline.
        """
        from django.utils import timezone

        # If the deadline date is declared
        if self.deadline_date:
            time_difference = str(self.deadline_date - timezone.now())[:-7]
            # Check if the time difference is a negative value
            if time_difference[0] == '-':
                return 'Overdue'
            else:
                return time_difference
        else:
            return "Open"


class TaskRate(models.Model):

    id = models.AutoField(primary_key=True)
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    on_time_rate = models.FloatField()
    rate = models.FloatField()

    def __str__(self) -> str:
        return str(self.rate)


class Week(models.Model):

    id = models.AutoField(primary_key=True)
    week_start_date = models.DateField(null=True, blank=True)
    week_end_date = models.DateField(null=True, blank=True)
    is_rated = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self) -> str:
        return f'Week {self.id}'

    @classmethod
    def getLastWeekID(cls) -> int:
        """
        If there is no weeks added yet this function will return -1 
        else will return the ID of the last week added and have been rated

        Returns:
            int: Last week ID, -1 if there is no weeks added or rated
        """
        if not cls.objects.filter(is_rated=True).exists():
            return -1
        return cls.objects.filter(is_rated=True).order_by('-id')[0].id


class WeeklyRate(models.Model):

    id = models.AutoField(primary_key=True)
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL,
                                 null=True, blank=True)
    rate = models.FloatField()

    def __str__(self) -> str:
        return str(self.rate)
