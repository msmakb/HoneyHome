from typing import Union

from django.contrib.auth.models import User
from django.db import models
from django.http import HttpRequest

from main.models import BaseModel, Person
from warehouse_admin.models import ItemType, Batch, Stock


class Distributor(BaseModel):

    id = models.AutoField(primary_key=True)
    person = models.ForeignKey(
        Person, on_delete=models.SET_NULL, null=True, blank=True)
    account = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    stock = models.OneToOneField(
        Stock, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return self.person.name

    def setPerson(self, requester: Union[HttpRequest, str], person: Person) -> None:
        self.person = person
        self.setCreatedByUpdatedBy(requester)

    def setAccount(self, requester: Union[HttpRequest, str], account: User) -> None:
        self.account = account
        self.setCreatedByUpdatedBy(requester)

    def setStock(self, requester: Union[HttpRequest, str], stock: Stock) -> None:
        self.stock = stock
        self.setCreatedByUpdatedBy(requester)

    @property
    def getId(self) -> int:
        return self.id

    @property
    def getPerson(self) -> Person:
        return self.person

    @property
    def getAccount(self) -> User:
        return self.account

    @property
    def getStock(self) -> Stock:
        return self.stock


class SalesHistory(BaseModel):
    id = models.AutoField(primary_key=True)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    type = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
    receiving_date = models.DateField(null=True, blank=True)
    received_from = models.CharField(max_length=50, null=True, blank=True)
    payment_date = models.DateField(auto_now_add=True)

    def getTotal(self):
        return self.price * self.quantity
