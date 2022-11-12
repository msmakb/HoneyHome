import logging as _logging
from typing import Union as _union

from .models import Parameter as _parameter

_logger = _logging.getLogger('HoneyHome.Main')


def _getDefaultParameters() -> dict:
    DEFAULT_PARAMETERS = {
        'ALLOWED_LOGGED_IN_ATTEMPTS': '5',  # -> int
        'ALLOWED_LOGGED_IN_ATTEMPTS_RESET': '1',  # -> int
        'MAX_TEMPORARY_BLOCK': '5',  # -> int
        'TEMPORARY_BLOCK_PERIOD': '1',  # -> int
        'TIME_OUT_PERIOD': '1440',  # -> int
        'BETWEEN_POST_REQUESTS_TIME': '500',  # -> int
        'MAGIC_NUMBER': '1',  # -> int
    }
    return DEFAULT_PARAMETERS


def _getParametersDescription() -> dict:
    DEFAULT_PARAMETERS = {
        'ALLOWED_LOGGED_IN_ATTEMPTS': 'Allowed login attempts before the user get blocked from the site. Note: IT MUST BE AN INTEGER.',
        'ALLOWED_LOGGED_IN_ATTEMPTS_RESET': 'This is the period of resetting the failed login attempt in days.  Note: IT MUST BE AN INTEGER.',
        'MAX_TEMPORARY_BLOCK': 'The number of temporary blocks of failing to login before getting blocked forever. Note: IT MUST BE AN INTEGER.',
        'TEMPORARY_BLOCK_PERIOD': 'The period of temporary block in days. Note: IT MUST BE AN INTEGER.',
        'TIME_OUT_PERIOD': 'Specifies the number of minutes before the Session time-out when logged in. The default is 1440 minutes, which is one day. Note: IT MUST BE AN INTEGER.',
        'BETWEEN_POST_REQUESTS_TIME': 'This is the milliseconds countdown before allowing the to do anther post request (1000 milliseconds = 1 second). Note: IT MUST BE AN INTEGER.',
        'MAGIC_NUMBER': 'DO NOT CHANGE THIS. THIS CONTROLLED BY THE SYSTEM ONLY.',
    }
    return DEFAULT_PARAMETERS


def _saveDefaultParametersToDataBase() -> None:
    # This executed one time only, when parameters table is created
    created_by = "System on Initialization"
    for name, value in _getDefaultParameters().items():
        if not _parameter.isExists(name=name):
            _parameter.create(
                created_by,
                name=name,
                value=value,
                description=_getParametersDescription().get(name, 'no description'),
            )


def getParameterValue(key: str) -> _union[str, int]:
    if key not in _getDefaultParameters():
        raise KeyError
    if not isinstance(key, str):
        raise ValueError
    try:
        try:
            param = int(_parameter.get(name=key).getValue)
            return param
        except ValueError:
            return _parameter.get(name=key).getValue
    except _parameter.DoesNotExist:
        _logger.warning(f"The parameter [{key}] dose not exist in database!!")
        try:
            param = int(_getDefaultParameters().get(key))
            return param
        except ValueError:
            return _getDefaultParameters().get(key)
