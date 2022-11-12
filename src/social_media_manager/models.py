from django.db import models
from main.models import BaseModel, Person
from warehouse_admin.models import ItemType


class Customer(BaseModel):
    id = models.AutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    instagram = models.CharField(
        max_length=20, default='-', null=True, blank=True)
    shopee = models.CharField(
        max_length=20, default='-', null=True, blank=True)
    facebook = models.CharField(
        max_length=20, default='-', null=True, blank=True)

    def __str__(self) -> str:
        return self.person.name


class CustomerPurchase(BaseModel):
    Stores = [
        ("Direct", "Direct"),
        ("instagram", "instagram"),
        ("shopee", "shopee"),
        ("facebook", "facebook"),
        ("Other", "Other")
    ]

    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    item = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    Purchase_from = models.CharField(max_length=10, choices=Stores)


class Questionnaire(BaseModel):
    STATUS = [
        ('Pending', 'Pending'),
        ('Running', 'Running'),
        ('Closed', 'Closed')
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)
    numbers_of_questions = models.IntegerField(
        default=0, null=True, blank=True)
    numbers_of_replies = models.IntegerField(default=0, null=True, blank=True)
    period = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS, default='Pending', null=True, blank=True)
    creation_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)


class SimpleQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    order = models.IntegerField()
    question = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.question


class SempleAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    question = models.ForeignKey(SimpleQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)


class ChoicesQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    order = models.IntegerField()
    question = models.CharField(max_length=255)
    choice_one = models.CharField(max_length=50)
    choice_two = models.CharField(max_length=50)
    choice_three = models.CharField(max_length=50)
    choice_four = models.CharField(max_length=50)
    choice_five = models.CharField(max_length=50)
    choice_six = models.CharField(max_length=50)
    choice_seven = models.CharField(max_length=50)
    choice_eight = models.CharField(max_length=50)
    choice_nine = models.CharField(max_length=50)
    choice_ten = models.CharField(max_length=50)


class ChoicesAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    question = models.ForeignKey(ChoicesQuestion, on_delete=models.CASCADE)
    choice_one = models.BooleanField(null=True, blank=True)
    choice_two = models.BooleanField(null=True, blank=True)
    choice_three = models.BooleanField(null=True, blank=True)
    choice_four = models.BooleanField(null=True, blank=True)
    choice_five = models.BooleanField(null=True, blank=True)
    choice_six = models.BooleanField(null=True, blank=True)
    choice_seven = models.BooleanField(null=True, blank=True)
    choice_eight = models.BooleanField(null=True, blank=True)
    choice_nine = models.BooleanField(null=True, blank=True)
    choice_ten = models.BooleanField(null=True, blank=True)
