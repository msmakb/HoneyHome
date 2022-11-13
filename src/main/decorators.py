import logging

from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import resolve

from distributor.models import Distributor
from human_resources.models import Employee

from . import constants
from . import messages as MSG
from .utils import getUserRole, resolvePageUrl

logger = logging.getLogger(constants.LOGGERS.MAIN)


def _getRequestFromViewArgs(args) -> HttpRequest:
    request = None
    for arg in args:
        if isinstance(arg, HttpRequest):
            request = arg
    if not request:
        raise TypeError("This is not a view function!")
    else:
        return request


def newEmployee(view_func):
    def wrapper_func(*args, **kwargs):
        request: HttpRequest = _getRequestFromViewArgs(args)
        path: str = resolve(request.path_info).url_name
        excluded_pages: tuple[str] = (constants.PAGES.CREATE_USER_PAGE,
                                      constants.PAGES.UNAUTHORIZED_PAGE,
                                      constants.PAGES.LOGOUT)
        if request.user.is_authenticated and path not in excluded_pages:
            if getUserRole(request) == constants.ROLES.DISTRIBUTOR:
                name: str = Distributor.get(
                    account=request.user).person.name
            else:
                name: str = Employee.get(
                    account=request.user).person.name
            # The initial username will be the employee/distributor first name
            first_name = name.split(' ')[0]
            new_employee: bool = request.user.username == first_name
            if new_employee:
                MSG.WELCOME_MESSAGE(request, first_name)
                MSG.TEMPORARY_ACCOUNT(request)
                MSG.CREATE_NEW_ACCOUNT(request)
                logger.info(f"The user [{first_name}] must create new account")
                return redirect(constants.PAGES.CREATE_USER_PAGE)
            else:
                return view_func(*args, **kwargs)
        else:
            return view_func(*args, **kwargs)
    return wrapper_func


def isAuthenticatedUser(view_func):
    def wrapper_func(*args, **kwargs):
        request: HttpRequest = _getRequestFromViewArgs(args)
        if request.user.is_authenticated:
            logger.info(
                f"The user [{request.user.username}] is authenticated")
            role: str = ''
            if request.user.groups.exists():
                role = getUserRole(request)
                # Remove spaces and add dashboard
                dashboard = role.replace(' ', '') + constants.PAGES.DASHBOARD
                logger.info("Redirect the user to his dashboard")
            else:
                logger.warning("The user has no groups!!")
                MSG.SOMETHING_WRONG(request)
                return redirect(f"{role}:{constants.PAGES.LOGOUT}")
            return redirect(resolvePageUrl(request, dashboard))
        else:
            return view_func(*args, **kwargs)
    return wrapper_func
