from django.db import models
from . import constant


class Person(models.Model):

    id = models.AutoField(primary_key=True)
    photo = models.ImageField(upload_to='photographs', null=True, blank=True)
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=constant.CHOICES.GENDER,
                              null=True, blank=True)
    nationality = models.CharField(max_length=10, choices=constant.CHOICES.COUNTRY,
                                   null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    contacting_email = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    register_date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
