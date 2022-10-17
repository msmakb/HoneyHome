from django.contrib.auth.models import Group
from human_resources.models import Employee
from . import constant


def createGroups(**kwargs):
    """
    This function creates all groups after migrating all database models
    Also it will create the CEO object.
    """
    if not Group.objects.all().exists():
        for name in constant.ROLES:
            group = Group.objects.create(name=name)
            print(f"  {group} group was created.")

        Employee.objects.create(position="CEO")
