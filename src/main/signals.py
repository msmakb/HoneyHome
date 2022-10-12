from django.contrib.auth.models import Group
from human_resources.models import Employee


def createGroups(**kwargs):
    """
    This function creates all groups after migrating all database models
    Also it will create the CEO object.
    """
    if not Group.objects.all().exists():
        GROUPS = (
            'Accounting Manager',
            'Admin',
            'CEO',
            'Designer',
            'Distributor',
            'Human Resources',
            'Social Media Manager',
            'Warehouse Admin',
        )

        for name in GROUPS:
            group = Group.objects.create(name=name)
            print(f"  {group} group was created.")

        Employee.objects.create(position="CEO")
