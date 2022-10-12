from django.contrib.auth.models import User, Group
from main.models import Person
from warehouse_admin.models import Stock
from .models import TaskRate


def createUserAccount(person: object, is_ceo=False):
    """
    Crete new user account for the employees and distributors

    Args:
        person (object): Person object
        is_ceo (bool, optional): True if it is CEO. Defaults to False.
    """
    if is_ceo:
        # Create super user for the ceo
        User.objects.create_superuser(
            username=person.name,
            password=person.name,
        ).save()
    else:
        # Create new user
        User.objects.create_user(username=str(person.name).split(' ')[0],
                                 email=person.contacting_email,
                                 password=str(person.name).split(' ')[0],
                                 first_name=str(person.name).split(' ')[0],
                                 last_name=str(person.name).split(' ')[-1],
                                 ).save()


def onAddingUpdatingEmployee(sender, instance, created, **kwargs):
    """
    This function called every time a new employee added.
    It creates a user account and assigns the person object to the employee.
    Also it will be called if the object has been updated.
    The if statement checks if the 
    """
    if created:
        # If not CEO
        if instance.position != "CEO":
            person = Person.objects.all().order_by('-id')[0]
            createUserAccount(person)
            account = User.objects.all().order_by('-id')[0]
            # The position of the Employee
            Group.objects.get(name=instance.position).user_set.add(account)
            instance.account = account
            instance.person = person
            instance.save()
        else:
            # If CEO. This will be initialized on migrating
            Person.objects.create(name="CEO").save()
            person = Person.objects.all()[0]
            createUserAccount(person, is_ceo=True)
            super_user = User.objects.all()[0]
            # Print in console during migrating
            print(f"  Super User '{super_user.username}' was created.")
            Group.objects.get(name=instance.position).user_set.add(super_user)
            # Print in console during migrating
            print(f"  The super user added to CEO group.")
            instance.account = super_user
            instance.person = person
            instance.save()
    # On update
    else:
        # delete the employee group
        instance.account.groups.clear()
        # assigning the employee with the new position
        Group.objects.get(name=instance.position
                          ).user_set.add(instance.account)


def onAddingUpdatingDistributor(sender, instance, created, **kwargs):
    """
    This function called every time a new distributor added.
    It creates a user account, assigns the person object to the distributor, 
    and creates a new stock object to the distributor. 
    """
    if created:
        person = Person.objects.all().order_by('-id')[0]
        createUserAccount(person)
        account = User.objects.all().order_by('-id')[0]
        # Setting the distributor groupe
        Group.objects.get(name="Distributor").user_set.add(account)
        # Create new stock object for the distributor
        Stock.objects.create()
        stock = Stock.objects.all().order_by('-id')[0]
        # Assigning the objects to the distributor
        instance.account = account
        instance.person = person
        instance.stock = stock
        instance.save()


def deleteUserAccount(sender, instance, using, **kwargs):
    """
    Delete the employee/distributor user account before the employee object
    """
    instance.account.delete()


def deleteTaskRate(sender, instance, using, **kwargs):
    """
    Delete the task rate before the task object getting deleted
    """
    try:
        task_rate = TaskRate.objects.get(task=instance)
        task_rate.delete()
    except TaskRate.DoesNotExist:
        pass
