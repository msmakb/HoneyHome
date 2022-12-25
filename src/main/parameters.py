from dataclasses import dataclass
import logging as logging
from logging import Logger
from typing import Union

from .constants import ACCESS_TYPE, DATA_TYPE, LOGGERS
from .models import Parameter as _parameter

logger: Logger = logging.getLogger(LOGGERS.MAIN)


@dataclass
class _DefaultParameter:
    name: str
    value: str
    access_type: str
    parameter_type: str
    description: str


def _getDefaultParam() -> list[_DefaultParameter]:
    default_parameters: list[_DefaultParameter] = list()
    default_parameters.append(
        _DefaultParameter(
            name="ALLOWED_LOGGED_IN_ATTEMPTS",
            value="5",
            description="Allowed login attempts before the user get blocked from the site. Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="ALLOWED_LOGGED_IN_ATTEMPTS_RESET",
            value="1",
            description="This is the period of resetting the failed login attempt in days.  Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="MAX_TEMPORARY_BLOCK",
            value="5",
            description="The number of temporary blocks of failing to login before getting blocked forever. Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="TEMPORARY_BLOCK_PERIOD",
            value="1",
            description="The period of temporary block in days. Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="TIME_OUT_PERIOD",
            value="1440",
            description="Specifies the number of minutes before the Session time-out when logged in. The default is 1440 minutes, which is one day. Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="BETWEEN_POST_REQUESTS_TIME",
            value="500",
            description="This is the milliseconds countdown before allowing the to do anther post request (1000 milliseconds = 1 second). Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="MAGIC_NUMBER",
            value="1",
            description="DO NOT CHANGE THIS. THIS CONTROLLED BY THE SYSTEM ONLY.",
            access_type=ACCESS_TYPE.No_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="WEEKLY_RATE_TASK_NAME",
            value="Evaluate employees",
            description="The name of the task given to the HR to rate the employees.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.STRING
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="WEEKLY_RATE_TASK_DESCRIPTION",
            value="Make sure to rate each employee on their weekly evaluations.",
            description="The description of the task given to the HR to rate the employees.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.STRING
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="WEEKLY_RATE_TASK_PERIOD",
            value="7",
            description="The period in days to submit the task given to the HR to rate the employees. Note: IT MUST BE AN INTEGER.",
            access_type=ACCESS_TYPE.ADMIN_ACCESS,
            parameter_type=DATA_TYPE.INTEGER
        )
    )
    default_parameters.append(
        _DefaultParameter(
            name="TEST",
            value="TEST_PARAMETER",
            description="Just for testing propose.",
            access_type=ACCESS_TYPE.No_ACCESS,
            parameter_type=DATA_TYPE.STRING
        )
    )
    return default_parameters


def _saveDefaultParametersToDataBase() -> None:
    # This executed one time only, when parameters table is created
    created_by = "System on Initialization"
    for pram in _getDefaultParam():
        if pram.name == "TEST":
            continue
        if not _parameter.isExists(name=pram.name):
            logger.info(f"The default parameter {pram.name}"
                        + " added to the database.")
            _parameter.create(
                created_by,
                name=pram.name,
                value=pram.value,
                description=pram.description,
                access_type=pram.access_type,
                parameter_type=pram.parameter_type,
            )


def getParameterValue(key: str) -> Union[str, int, float, bool]:
    if not isinstance(key, str):
        raise ValueError("The key must be a string.")
    try:
        param: _parameter = _parameter.get(name=key)
        match param.getParameterType:
            case DATA_TYPE.INTEGER:
                value: int = int(param.getValue)
                return value
            case DATA_TYPE.FLOAT:
                value: float = float(param.getValue)
                return value
            case DATA_TYPE.BOOLEAN:
                val: str = param.getValue
                true_con: tuple[bool, ...] = (
                    val.lower() == 'yes',
                    val.lower() == 'true',
                    val == '1',
                )
                false_con: tuple[bool, ...] = (
                    val.lower() == 'no',
                    val.lower() == 'false',
                    val == '0'
                )
                if any(true_con):
                    return True
                elif any(false_con):
                    return False
                else:
                    raise ValueError
            case _:
                return param.getValue
    except _parameter.DoesNotExist:
        if key != "TEST":
            logger.warning(f"The parameter [{key}] "
                           + "dose not exist in database!")
        for pram in _getDefaultParam():
            if key == pram.name:
                match pram.parameter_type:
                    case DATA_TYPE.INTEGER:
                        value: int = int(pram.value)
                        return value
                    case DATA_TYPE.FLOAT:
                        value: float = float(pram.value)
                        return value
                    case DATA_TYPE.BOOLEAN:
                        val: str = pram.value
                        true_con: tuple[bool, ...] = (
                            val.lower() == 'yes',
                            val.lower() == 'true',
                            val == '1',
                        )
                        false_con: tuple[bool, ...] = (
                            val.lower() == 'no',
                            val.lower() == 'false',
                            val == '0'
                        )
                        if any(true_con):
                            return True
                        elif any(false_con):
                            return False
                        else:
                            raise ValueError
                    case _:
                        return pram.value
        raise KeyError("The parameter does not exist in the database "
                       + "nor the default parameters.")
