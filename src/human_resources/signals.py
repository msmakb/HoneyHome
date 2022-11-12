from typing import Optional, Union

from django.contrib.auth.models import User, Group

from distributor.models import Distributor
from main import constants
from main.models import Person
from warehouse_admin.models import Stock

from .models import Task, TaskRate, Employee


def _createUserAccount(person: Person, is_ceo: Optional[bool] = False) -> User:
    """
    Crete new user account for the employees and distributors

    Args:
        person (object): Person object
        is_ceo (bool, optional): True if it is CEO. Defaults to False.
    """
    first_name = person.name.split(' ')[0]
    last_name = person.name.split(' ')[-1]
    if is_ceo:
        # Create super user for the ceo
        account = User.objects.create_superuser(
            username=first_name,
            password=first_name,
            first_name=first_name,
            last_name=last_name,
        )
    else:
        # Create normal user
        account = User.objects.create_user(
            username=first_name,
            email=person.contacting_email,
            password=first_name,
            first_name=first_name,
            last_name=last_name,
        )
    return account


def onAddingUpdatingEmployee(sender: Employee, instance: Employee, created: bool, **kwargs):
    """
    This function called every time a new employee added.
    It creates a user account and assigns the person object to the employee.
    Also it will be called if the object has been updated.
    The if statement checks if the 
    """
    if created:
        if instance.position != constants.ROLES.CEO:
            person: Person = Person.getLastInsertedObject()
            account = _createUserAccount(person)
            Group.objects.get(name=instance.position).user_set.add(account)
            instance.account = account
            instance.person = person
            instance.save()
        else:
            Person.objects.create(name=constants.ROLES.CEO)
            person: Person = Person.getLastInsertedObject()
            super_user = _createUserAccount(person, is_ceo=True)
            print(f"  Super User '{super_user.username}' was created.")
            Group.objects.get(name=instance.position).user_set.add(super_user)
            print(f"  The super user added to CEO group.")
            instance.account = super_user
            instance.person = person
            instance.save()
    # On update
    else:
        # assigning the employee with the new specified position
        instance.account.groups.clear()
        Group.objects.get(name=instance.position
                          ).user_set.add(instance.account)


def onAddingUpdatingDistributor(sender: Distributor, instance: Distributor, created: bool, **kwargs):
    """
    This function called every time a new distributor added.
    It creates a user account, assigns the person object to the distributor, 
    and creates a new stock object to the distributor. 
    """
    if created:
        person: Person = Person.getLastInsertedObject()
        account = _createUserAccount(person)
        Group.objects.get(
            name=constants.ROLES.DISTRIBUTOR).user_set.add(account)
        stock = Stock.create(constants.SYSTEM_SIGNALS_NAME)
        instance.account = account
        instance.person = person
        instance.stock = stock
        instance.save()


def deleteUserAccount(sender: Union[Employee, Distributor], instance: Union[Employee, Distributor], *args, **kwargs):
    """
    Delete the employee/distributor user account before the employee object
    """
    instance.account.delete()


def deleteTaskRate(sender: Task, instance: Task, *args, **kwargs):
    """
    Delete the task rate before the task object getting deleted
    """
    try:
        task_rate: TaskRate = TaskRate.get(task=instance)
        task_rate.delete(constants.SYSTEM_SIGNALS_NAME)
    except TaskRate.DoesNotExist:
        pass
