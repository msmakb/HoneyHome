import logging
from logging import Logger
from typing import Self, Union, Optional

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.timezone import datetime
from . import constants

logger: Logger = logging.getLogger(constants.LOGGERS.MODELS)


class BaseModel(models.Model):

    class Meta:
        abstract = True

    id: int = models.AutoField(primary_key=True)
    created: datetime = models.DateTimeField(auto_now_add=True)
    created_by: str = models.CharField(max_length=50, null=True, blank=True)
    updated: datetime = models.DateTimeField(auto_now=True)
    updated_by: str = models.CharField(max_length=50, null=True, blank=True)

    def setCreated(self, created: datetime) -> None:
        self.created = created
        self.save()

    def setCreatedBy(self, created_by: str) -> None:
        self.created_by = created_by
        self.save()

    def setUpdated(self, updated: datetime) -> None:
        self.updated = updated
        self.save()

    def setUpdatedBy(self, updated_by: str) -> None:
        self.updated_by = updated_by
        self.save()

    def setCreatedByUpdatedBy(self, requester: Union[HttpRequest, str], created: Optional[bool] = False) -> None:
        """
        This function if called, it must be called after the changes are made not before.
        """
        user: User = None
        requester_name: str = ''
        if not requester:
            requester_name = 'Unknown User'
        elif isinstance(requester, HttpRequest):
            user = requester.user
            if user.is_authenticated:
                requester_name = user.get_full_name()
            else:
                requester_name = user
        else:
            try:
                requester_name = str(requester)
            except Exception as exception:
                logger.error(exception)
                raise exception
        if created:
            self.created_by = requester_name
            self.updated_by = requester_name
            logger.info(
                f"Database change in [{self.__class__.__name__}] model "
                + f"adding new object. ID: {self.id} By: {user}")
        else:
            self.updated_by = requester_name
            logger.info(f"Database change in [{self.__class__.__name__}] "
                        + f"model at object ID: {self.id} By: {user}")
        self.save()

    @classmethod
    def create(cls, requester: Union[HttpRequest, str], *args, **kwargs) -> Self:
        obj: Self = cls.objects.create(*args, **kwargs)
        obj.setCreatedByUpdatedBy(requester, created=True)
        return obj

    def delete(self, requester: Union[HttpRequest, str], *args, **kwargs) -> tuple[int, dict[str, int]]:
        """
        Delete the object and loge the the changes.
        """
        requester_name: str = 'Unknown user'
        if not requester:
            # Do nothing and keep user is 'Unknown user'
            pass
        elif isinstance(requester, HttpRequest):
            user: User = requester.user
            if user.is_authenticated:
                requester_name = user.get_full_name()
            else:
                from .utils import getClientIp
                logger.warning(
                    f"Danger change detected from IP: {getClientIp(requester)}")
        else:
            try:
                requester_name = str(requester)
            except Exception as exception:
                logger.error(exception)
                raise exception

        logger.info(f"Database change in [{self.__class__.__name__}] model "
                    + f"object ID: [{self.id}] was deleted By: {requester_name}")
        return super().delete(*args, **kwargs)

    @classmethod
    def get(cls, *args, **kwargs) -> Self | None:
        """
        This will return None if there are multiple objects returned.
        """
        try:
            obj: Self = cls.objects.get(*args, **kwargs)
            return obj
        except cls.MultipleObjectsReturned:
            return None

    @classmethod
    def getAll(cls) -> QuerySet[Self]:
        """
        Get all objects stored in the database.
        """
        return cls.objects.all()

    @classmethod
    def getAllOrdered(cls, order_by: str, reverse: Optional[bool] = False) -> QuerySet[Self]:
        """
        Get all objects and order them.
        """
        if reverse:
            order_by = '-' + order_by
        return cls.objects.all().order_by(order_by)

    @classmethod
    def getLastInsertedObject(cls, queryset: Optional[QuerySet[Self]] = None) -> Self | None:
        """
        Get the last object from the model or queryset if it was declared.
        """
        query: QuerySet[Self] = queryset
        if queryset is not None:
            if not isinstance(queryset, QuerySet) or not isinstance(queryset.first(), cls):
                raise NotImplementedError
        else:
            query = cls.objects.all()
        try:
            return query.order_by('-id')[0]
        except IndexError:
            return None

    @classmethod
    def filter(cls, *args, **kwargs) -> QuerySet[Self]:
        return cls.objects.filter(*args, **kwargs)

    @classmethod
    def countAll(cls) -> int:
        """
        Count all objects.
        """
        return cls.objects.all().count()

    @classmethod
    def countFiltered(cls, *arg, **kwarg) -> int:
        """
        Count the filtered queryset.
        """
        return cls.objects.filter(*arg, **kwarg).count()

    @classmethod
    def orderFiltered(cls, order_by: str, *args, reverse=False, **kwargs) -> int:
        """
        Order the filtered queryset.
        """
        if reverse:
            order_by = '-' + order_by
        return cls.objects.filter(*args, **kwargs).order_by(order_by)

    @classmethod
    def isExists(cls, *arg, **kwarg) -> bool:
        """
        Tre if there is an object in the filtered queryset.
        """
        return cls.objects.filter(*arg, **kwarg).exists()


class Client(BaseModel):

    class Meta:
        abstract = True

    user_agent: str = models.CharField(max_length=256, null=True, blank=True)
    ip: str = models.GenericIPAddressField()

    def setUserAgent(self, requester: Union[HttpRequest, str], user_agent: str) -> None:
        self.user_agent = user_agent
        self.setCreatedByUpdatedBy(requester)

    def setIp(self, requester: Union[HttpRequest, str], ip: str) -> None:
        self.ip = ip
        self.setCreatedByUpdatedBy(requester)


class BlockedClient(Client):

    block_type: str = models.CharField(max_length=20,
                                       choices=constants.CHOICES.BLOCK_TYPE)
    blocked_times: int = models.PositiveSmallIntegerField(default=1)

    def __str__(self) -> str:
        return f"IP: {self.ip} - User Agent: {self.user_agent}"

    def setBlockType(self, requester: Union[HttpRequest, str], block_type: str) -> None:
        self.block_type = block_type
        self.setCreatedByUpdatedBy(requester)

    def setBlockedTimes(self, requester: Union[HttpRequest, str], blocked_times: int) -> None:
        self.blocked_times = blocked_times
        self.setCreatedByUpdatedBy(requester)


class AuditEntry(Client):

    action: str = models.CharField(max_length=50)
    username: str = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.action} - {self.username} - {self.ip}'

    def setAction(self, requester: Union[HttpRequest, str], action: str) -> None:
        self.action = action
        self.setCreatedByUpdatedBy(requester)

    def setUsername(self, requester: Union[HttpRequest, str], username: str) -> None:
        self.username = username
        self.setCreatedByUpdatedBy(requester)


class Parameter(BaseModel):
    """ 
    ---------------------------------------------------------
    #       There is no setters for parameter model         #
    #   Parameters can be set when the table is created     #
    #                see main.signals.py                    #
    #     And only can be modified via admin dashboard      #
    ---------------------------------------------------------
    """

    _name: str = models.CharField(max_length=50, editable=False,
                                  db_column='name', name='name')
    _value: str = models.CharField(max_length=50, db_column='value',
                                   name='value')
    _access_type: str = models.CharField(max_length=1, editable=False,
                                         db_column='access_type', name='access_type',
                                         choices=constants.CHOICES.ACCESS_TYPE,
                                         default=constants.ACCESS_TYPE.No_ACCESS)
    _parameter_type: str = models.CharField(max_length=1, editable=False,
                                            db_column='parameter_type', name='parameter_type',
                                            choices=constants.CHOICES.DATA_TYPE,
                                            default=constants.DATA_TYPE.STRING)
    _description: str = models.CharField(max_length=255, db_column='description',
                                         name='description', editable=False,
                                         null=True, blank=True)

    def __str__(self) -> str:
        return self.name.replace('_', ' ').capitalize()

    @property
    def getValue(self) -> str:
        return self.value

    @property
    def getParameterType(self) -> str:
        return self.parameter_type

    def clean(self) -> None:
        val: str = self.value
        match self.getParameterType:
            case constants.DATA_TYPE.INTEGER:
                try:
                    int(val)
                except ValueError:
                    raise ValidationError(
                        "Sorry, the value must be a integer.")
            case constants.DATA_TYPE.FLOAT:
                try:
                    float(val)
                except ValueError:
                    raise ValidationError("Sorry, the value must be a number.")
            case constants.DATA_TYPE.BOOLEAN:
                con: tuple[bool, ...] = (
                    val.lower() == 'yes',
                    val.lower() == 'no',
                    val.lower() == 'true',
                    val.lower() == 'false',
                    val == '1',
                    val == '0'
                )
                if not any(con):
                    raise ValidationError("Sorry, the value must be "
                                          + "('true' or 'false', 'yes' or 'no', '1' or '0')")

        return super().clean()


class Person(BaseModel):

    photo = models.ImageField(upload_to=constants.PERSONAL_PHOTOS_FOLDER,
                              null=True, blank=True)
    name: str = models.CharField(max_length=50)
    gender: str = models.CharField(max_length=6,
                                   choices=constants.CHOICES.GENDER)
    nationality: str = models.CharField(max_length=30,
                                        choices=constants.CHOICES.COUNTRY)
    date_of_birth: datetime = models.DateField(null=True, blank=True)
    address: str = models.CharField(max_length=255, null=True, blank=True)
    contacting_email: str = models.CharField(max_length=50,
                                             null=True, blank=True)
    phone_number: str = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    @property
    def getImageUrl(self) -> str | None:
        if not self.photo:
            return None
        return self.photo.url

    def setPhoto(self, requester: Union[HttpRequest, str], photo) -> None:
        self.photo = photo
        self.setCreatedByUpdatedBy(requester)
        return self.photo.url

    def setName(self, requester: Union[HttpRequest, str], name: str) -> None:
        self.name = name
        self.setCreatedByUpdatedBy(requester)

    def setGender(self, requester: Union[HttpRequest, str], gender: str) -> None:
        self.gender = gender
        self.setCreatedByUpdatedBy(requester)

    def setNationality(self, requester: Union[HttpRequest, str], nationality: str) -> None:
        self.nationality = nationality
        self.setCreatedByUpdatedBy(requester)

    def setDateOfBirth(self, requester: Union[HttpRequest, str], date_of_birth: datetime) -> None:
        self.date_of_birth = datetime.date(date_of_birth)
        self.setCreatedByUpdatedBy(requester)

    def setAddress(self, requester: Union[HttpRequest, str], address: str) -> None:
        self.address = address
        self.setCreatedByUpdatedBy(requester)

    def setContactingEmail(self, requester: Union[HttpRequest, str], contacting_email: str) -> None:
        self.contacting_email = contacting_email
        self.setCreatedByUpdatedBy(requester)

    def setPhoneNumber(self, requester: Union[HttpRequest, str], phone_number: str) -> None:
        self.phone_number = phone_number
        self.setCreatedByUpdatedBy(requester)
