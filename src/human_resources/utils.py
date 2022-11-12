from django.contrib.auth.models import User
from django.http import HttpRequest

from main import constants
from main.utils import getUserRole


def isUserAllowedToModify(user: User, employee_position_to_modify: str, employee_position: str) -> bool:
    if employee_position_to_modify == employee_position:
        if getUserRole(user) != constants.ROLES.CEO:
            return False
    return True


def isRequesterCEO(request: HttpRequest) -> bool:
    return True if getUserRole(request) == constants.ROLES.CEO else False
