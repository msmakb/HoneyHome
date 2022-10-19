from django.contrib import messages
from django.shortcuts import redirect

from distributor.models import Distributor
from human_resources.models import Employee
from .utils import getUserRole
from . import constant


def _newEmployee(request) -> bool:
    if getUserRole(request) == constant.ROLES.DISTRIBUTOR:
        name: str = Distributor.objects.get(account=request.user).getName()
    else:
        name: str = Employee.objects.get(account=request.user).getName()
    new_employee: bool = request.user.username == name.split(' ')[0]
    if new_employee:
        messages.success(
            request, f"Hello, {name}. Welcome to Honey Home System.")
        messages.success(
            request, f"This account you singed in is a temporary account.")
        messages.success(
            request, f"Please create new account with your personal information.")
        return True
    return False


def isAuthenticatedUser(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if _newEmployee(request):
                return redirect(constant.PAGES.CREATE_USER_PAGE)
            role: str = ''
            if request.user.groups.exists():
                role = getUserRole(request)
                g = role.split(' ')
                role = ''
                for i in g:
                    role += i
            return redirect(role + constant.PAGES.DASHBOARD)
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowedUsers(allowed_roles: list = []):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            role: str = ''
            if request.user.groups.exists():
                if _newEmployee(request):
                    return redirect(constant.PAGES.CREATE_USER_PAGE)
                role = getUserRole(request)
            if role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return redirect(constant.PAGES.UNAUTHORIZED_PAGE)
        return wrapper_func
    return decorator
