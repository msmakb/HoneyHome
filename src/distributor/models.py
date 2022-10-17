from django.contrib.auth.models import User
from django.db import models
from main.models import Person
from warehouse_admin.models import ItemType, Batch, Stock


class Distributor(models.Model):
    id = models.AutoField(primary_key=True)
    person = models.ForeignKey(
        Person, on_delete=models.SET_NULL, null=True, blank=True)
    account = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    stock = models.OneToOneField(
        Stock, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return self.person.name

    def getPhotoUrl(self) -> str:
        return self.person.photo.url

    def getName(self) -> str:
        return self.person.name

    def getGender(self) -> str:
        return self.person.gender

    def getNationality(self) -> str:
        return self.person.nationality

    def getDateOfBirth(self) -> str:
        return self.person.date_of_birth

    def getAddress(self) -> str:
        return self.person.address

    def getContactingEmail(self) -> str:
        return self.person.contacting_email

    def getPhoneNumber(self) -> str:
        return self.person.phone_number

    def getRegisteringDate(self) -> str:
        return self.person.register_date


class SalesHistory(models.Model):
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
