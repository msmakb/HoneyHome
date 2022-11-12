import logging

from django.contrib.auth.models import Group

from human_resources.models import Employee

from . import constants
from .models import AuditEntry
from .utils import getClientIp, getUserAgent

logger = logging.getLogger(constants.LOGGERS.MAIN)


def createGroups(**kwargs):
    if not Group.objects.all().exists():
        for name in constants.ROLES:
            group = Group.objects.create(name=name)
            print(f"  {group} group was created.")
        logger.info("All default groups was successfully created.")
        Employee.create(constants.SYSTEM_NAME, position=constants.ROLES.CEO)


def createParameters(**kwargs):
    from .parameters import _saveDefaultParametersToDataBase
    _saveDefaultParametersToDataBase()
    logger.info("All default parameters was successfully created.")


def userLoggedIn(sender, request, user, **kwargs):
    ip = getClientIp(request)
    AuditEntry.create(constants.SYSTEM_NAME,
                      action=constants.ACTION.LOGGED_IN,
                      user_agent=getUserAgent(request),
                      ip=ip,
                      username=user.username)
    logger.info(f'Login user: {user} via ip: {ip}')


def userLoggedOut(sender, request, user, **kwargs):
    ip = getClientIp(request)
    AuditEntry.create(constants.SYSTEM_NAME,
                      action=constants.ACTION.LOGGED_OUT,
                      user_agent=getUserAgent(request),
                      ip=ip,
                      username=user.username)
    logger.info(f'Logout user: {user} via ip: {ip}')


def userLoggedFailed(sender, credentials, **kwargs):
    request = kwargs.get('request')
    ip = getClientIp(request)
    AuditEntry.create(constants.SYSTEM_NAME,
                      action=constants.ACTION.LOGGED_FAILED,
                      user_agent=getUserAgent(request),
                      ip=ip,
                      username=credentials.get('username', None))
    logger.warning(f'Failed accessed to login using: {credentials}')
