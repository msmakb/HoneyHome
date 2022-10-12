from urllib import request
from django.contrib import messages
from django.shortcuts import redirect

from distributor.models import Distributor
from human_resources.models import Employee


def newEmployee(request):
    if request.user.groups.all()[0].name == "Distributor":
        name = Distributor.objects.get(account=request.user).person.name
    else:
        name = Employee.objects.get(account=request.user).person.name
    new_employee = request.user.username == str(
        name).split(' ')[0]
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
            if newEmployee(request):
                return redirect('CreateUserPage')
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                if group == 'Admin':
                    return redirect('Dashboard')
                g = str(group).split(' ')
                group = ''
                for i in g:
                    group += i
            return redirect(group + 'Dashboard')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                if newEmployee(request):
                    return redirect('CreateUserPage')
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('Unauthorized')
        return wrapper_func
    return decorator
