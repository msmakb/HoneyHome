import logging
from typing import Union, Optional

from django.contrib.auth.models import User
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils import timezone

from . import constants

logger = logging.getLogger(constants.LOGGERS.MODELS)


class BaseModel(models.Model):

    class Meta:
        abstract = True

    id: int = models.AutoField(primary_key=True)
    created: timezone.datetime = models.DateTimeField(auto_now_add=True)
    created_by: str = models.CharField(max_length=50, null=True, blank=True)
    updated: timezone.datetime = models.DateTimeField(auto_now=True)
    updated_by: str = models.CharField(max_length=50, null=True, blank=True)

    def setCreated(self, created: timezone.datetime):
        self.created = created
        self.save()

    def setCreatedBy(self, created_by: str):
        self.created_by = created_by
        self.save()

    def setUpdated(self, updated: timezone.datetime):
        self.updated = updated
        self.save()

    def setUpdatedBy(self, updated_by: str):
        self.updated_by = updated_by
        self.save()

    def setCreatedByUpdatedBy(self, requester: Union[HttpRequest, str], created: Optional[bool] = False) -> None:
        """
        This function if called, it must be called after the changes not before
        """
        user: User = None
        requester_name: str = ''
        obj: BaseModel = self
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
            obj = self.getLastInsertedObject()
            obj.created_by = requester_name
            obj.updated_by = requester_name
            logger.info(
                f"Database change in [{obj.__class__.__name__}] model "
                + f"adding new object. ID: {obj.id} By: {user}")
        else:
            obj.updated_by = requester_name
            logger.info(f"Database change in [{obj.__class__.__name__}] "
                        + f"model at object ID: {obj.id} By: {user}")
        obj.save()

    @classmethod
    def create(cls, requester: Union[HttpRequest, str], *args, **kwargs):
        obj = cls.objects.create(*args, **kwargs)
        cls.setCreatedByUpdatedBy(cls, requester, created=True)
        return obj

    def delete(self, requester: Union[HttpRequest, str], *args, **kwargs) -> None:
        user = 'Unknown user'
        if not requester:
            # Do nothing and keep user is 'Unknown user'
            pass
        elif isinstance(requester, HttpRequest):
            if requester.user.is_authenticated:
                user = requester.user.first_name + " " + requester.user.last_name
            else:
                from .utils import getClientIp
                logger.critical(
                    f"Danger change detected from IP: {getClientIp(requester)}")
        else:
            try:
                user = str(requester)
            except Exception as exception:
                logger.error(exception)
                raise exception

        logger.info(f"Database change in [{self.__class__.__name__}] model "
                    + f"object ID: [{self.id}] was deleted By: {user}")
        return super().delete(*args, **kwargs)

    @classmethod
    def get(cls, *args, **kwargs):
        try:
            obj = cls.objects.get(*args, **kwargs)
            return obj
        except cls.MultipleObjectsReturned:
            return None

    @classmethod
    def getAll(cls) -> QuerySet:
        return cls.objects.all()

    @classmethod
    def getAllOrdered(cls, order_by: str, reverse: Optional[bool] = False) -> QuerySet:
        if reverse:
            order_by = '-' + order_by
        return cls.objects.all().order_by(order_by)

    @classmethod
    def getLastInsertedObject(cls, queryset: Optional[QuerySet] = None):
        query: QuerySet = queryset
        if queryset is not None:
            if not isinstance(queryset, QuerySet):
                raise NotImplementedError
        else:
            query = cls.objects.all()
        try:
            return query.order_by('-id')[0]
        except IndexError:
            return None

    @classmethod
    def filter(cls, *args, **kwargs) -> QuerySet:
        return cls.objects.filter(*args, **kwargs)

    @classmethod
    def countAll(cls) -> int:
        return cls.objects.all().count()

    @classmethod
    def countFiltered(cls, *arg, **kwarg) -> int:
        return cls.objects.filter(*arg, **kwarg).count()

    @classmethod
    def orderFiltered(cls, order_by: str, *args, reverse=False, **kwargs) -> int:
        if reverse:
            order_by = '-' + order_by
        return cls.objects.filter(*args, **kwargs).order_by(order_by)

    @classmethod
    def isExists(cls, *arg, **kwarg) -> bool:
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

    # There is no setters for parameter model
    # Parameters can be set when the table is created _
    # _ see main.signals.py
    # And only can be modified via admin dashboard
    _name: str = models.CharField(max_length=50, editable=False,
                                  db_column='name', name='name')
    _value: str = models.CharField(max_length=50, db_column='value',
                                   name='value')
    _description: str = models.CharField(max_length=255, db_column='description',
                                         name='description', editable=False,
                                         null=True, blank=True)

    @property
    def getName(self) -> str:
        return self.name

    @property
    def getValue(self) -> str:
        return self.value

    @property
    def getDescription(self) -> str:
        return self.description


class Person(BaseModel):

    photo = models.ImageField(upload_to=constants.PERSONAL_PHOTOS_FOLDER,
                              null=True, blank=True)
    name: str = models.CharField(max_length=50)
    gender: str = models.CharField(max_length=6,
                                   choices=constants.CHOICES.GENDER)
    nationality: str = models.CharField(max_length=30,
                                        choices=constants.CHOICES.COUNTRY)
    date_of_birth: timezone.datetime = models.DateField(null=True, blank=True)
    address: str = models.CharField(max_length=255, null=True, blank=True)
    contacting_email: str = models.CharField(max_length=50,
                                             null=True, blank=True)
    phone_number: str = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    @property
    def getImageUrl(self) -> str:
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

    def setDateOfBirth(self, requester: Union[HttpRequest, str], date_of_birth: timezone.datetime) -> None:
        self.date_of_birth = timezone.datetime.date(date_of_birth)
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
