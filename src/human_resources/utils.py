from django.contrib.auth.models import User
from main import constant
from main.utils import getUserRole


def isUserAllowedToModify(user: User, employee_position_to_modify: str, employee_position: str) -> bool:
    """
    Check if the user is the allowed to view or modify data.
    Ex: the user cannot modify his own data.

    Args:
        user (User): The user
        employee_position_to_modify (str): The employee position to check if it's able to modify
        employee_position (str): The employee position

    Returns:
        bool: True if the user is CEO; otherwise, False
    """
    # Check if it's CEO page.
    if employee_position_to_modify == employee_position:
        # if it's CEO page it cannot be changed by anyone except the CEO
        if getUserRole(user) != constant.ROLES.CEO:
            # If the user is not CEO redirect him
            return False

    return True


def isRequesterCEO(request):
    return True if getUserRole(request) == constant.ROLES.CEO else False
