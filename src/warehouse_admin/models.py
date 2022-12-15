from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.timezone import datetime

from main import constants
from main.models import BaseModel


class Batch(BaseModel):

    name: str = models.CharField(max_length=20, unique=True)
    code: str = models.CharField(max_length=30, unique=True)
    arrival_date: datetime.date = models.DateField(null=True, blank=True)
    quantity: int = models.PositiveIntegerField()
    description: str = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def getAvailableQuantity(self) -> int:
        batch_cards: QuerySet[ItemCard] = ItemCard.filter(batch=self)
        used_quantity: int = 0
        for card in batch_cards:
            used_quantity += card.quantity
        return self.quantity - used_quantity

    def setName(self, request: HttpRequest, name: str) -> None:
        self.name = name
        self.setCreatedByUpdatedBy(request)

    def setCode(self, request: HttpRequest, code: str) -> None:
        self.code = code
        self.setCreatedByUpdatedBy(request)

    def setArrivalDate(self, request: HttpRequest, arrival_date: datetime.date) -> None:
        self.arrival_date = arrival_date
        self.setCreatedByUpdatedBy(request)

    def setQuantity(self, request: HttpRequest, quantity: int) -> None:
        self.quantity = quantity
        self.setCreatedByUpdatedBy(request)

    def setDescription(self, request: HttpRequest, description: str) -> None:
        self.description = description
        self.setCreatedByUpdatedBy(request)


class ItemType(BaseModel):

    name: str = models.CharField(max_length=30, unique=True)
    code: str = models.CharField(max_length=10, unique=True)
    weight: int = models.IntegerField()
    is_retail: bool = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    def setName(self, request: HttpRequest, name: str) -> None:
        self.name = name
        self.setCreatedByUpdatedBy(request)

    def setCode(self, request: HttpRequest, code: str) -> None:
        self.code = code
        self.setCreatedByUpdatedBy(request)

    def setWeight(self, request: HttpRequest, weight: str) -> None:
        self.weight = weight
        self.setCreatedByUpdatedBy(request)

    def setRetail(self, request: HttpRequest, is_retail: str) -> None:
        self.is_retail = is_retail
        self.setCreatedByUpdatedBy(request)


class Stock(BaseModel):

    def __str__(self) -> str:
        stock: str = ''
        if self.id == constants.MAIN_STORAGE_ID:
            stock = constants.MAIN_STORAGE_NAME
        else:
            try:
                from distributor.models import Distributor
                distributor: Distributor = Distributor.get(stock=self.id)
                stock = distributor.person.name.split(' ')[0]
            except Distributor.DoesNotExist:
                return super().__str__()
        return stock + " Stock"

    def getTotalGoodsInStock(self):
        total: int = 0
        item_cards: QuerySet[ItemCard] = ItemCard.filter(
            stock=self, is_transforming=False, )  # is_priced=True)
        for item in item_cards:
            total += item.quantity

        return total


class ItemCard(BaseModel):

    type: ItemType = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    batch: Batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    stock: Stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity: int = models.PositiveIntegerField()
    status: str = models.CharField(max_length=10, default=constants.ITEM_STATUS.GOOD,
                                   choices=constants.CHOICES.ITEM_STATUS)
    price: float = models.FloatField(null=True, blank=True)
    received_from: str = models.CharField(default=constants.COUNTRY.get("YEMEN"),
                                          max_length=50)
    is_transforming: bool = models.BooleanField(default=False)
    is_priced: bool = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.type.name}-{self.batch.name}'

    @property
    def receiving_date(self) -> datetime:
        return self.created.date()

    @property
    def receiver(self) -> str:
        if self.stock.id == constants.MAIN_STORAGE_ID:
            return None
        else:
            try:
                from distributor.models import Distributor
                distributor: Distributor = Distributor.get(stock=self.stock)
                return distributor.person.name
            except Distributor.DoesNotExist:
                return None

    @property
    def total_price(self) -> float:
        return self.price * self.quantity

    def getDistributor(self):
        if self.stock.id == constants.MAIN_STORAGE_ID:
            return None
        else:
            try:
                from distributor.models import Distributor
                distributor: Distributor = Distributor.get(stock=self.stock)
                return distributor
            except Distributor.DoesNotExist:
                return None

    def setType(self, request: HttpRequest, type: ItemType) -> None:
        self.type = type
        self.setCreatedByUpdatedBy(request)

    def setBatch(self, request: HttpRequest, batch: Batch) -> None:
        self.batch = batch
        self.setCreatedByUpdatedBy(request)

    def setStock(self, request: HttpRequest, stock: Stock) -> None:
        self.stock = stock
        self.setCreatedByUpdatedBy(request)

    def setQuantity(self, requester: HttpRequest, quantity: int) -> None:
        self.quantity = quantity
        self.setCreatedByUpdatedBy(requester)

    def setStatus(self, request: HttpRequest, status: str) -> None:
        self.status = status
        self.setCreatedByUpdatedBy(request)

    def setPrice(self, request: HttpRequest, price: str) -> None:
        self.price = price
        self.setCreatedByUpdatedBy(request)

    def setReceivedFrom(self, request: HttpRequest, received_from: str) -> None:
        self.received_from = received_from
        self.setCreatedByUpdatedBy(request)

    def setTransforming(self, request: HttpRequest, is_transforming: str) -> None:
        self.is_transforming = is_transforming
        self.setCreatedByUpdatedBy(request)

    def setPriced(self, request: HttpRequest, is_priced: str) -> None:
        self.is_priced = is_priced
        self.setCreatedByUpdatedBy(request)


class RetailCard(BaseModel):

    type: ItemType = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    weight: int = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f'{self.type.name}'

    @property
    def conversion_date(self) -> datetime:
        return self.created


class RetailItem(BaseModel):

    type: ItemType = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    quantity: int = models.PositiveIntegerField()
    price: int = models.FloatField()

    def __str__(self) -> str:
        return f'{self.type.name}-{self.type.weight}'

    def setType(self, request: HttpRequest, type: str) -> None:
        self.type = type
        self.setCreatedByUpdatedBy(request)

    def setQuantity(self, request: HttpRequest, quantity: str) -> None:
        self.quantity = quantity
        self.setCreatedByUpdatedBy(request)

    def setPrice(self, request: HttpRequest, price: str) -> None:
        self.price = price
        self.setCreatedByUpdatedBy(request)


class GoodsMovement(BaseModel):

    item: str = models.CharField(max_length=30)
    code: str = models.CharField(max_length=10)
    batch: str = models.CharField(max_length=20)
    quantity: int = models.PositiveIntegerField()
    status: str = models.CharField(max_length=10, default=constants.ITEM_STATUS.GOOD,
                                   choices=constants.CHOICES.ITEM_STATUS)
    sender: str = models.CharField(max_length=50)
    receiver: str = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.item} from {self.sender} to {self.receiver} at {self.date}"

    @property
    def date(self) -> datetime:
        return self.created.date()

    def setItem(self, request: HttpRequest, item: str) -> None:
        self.item = item
        self.setCreatedByUpdatedBy(request)

    def setSender(self, request: HttpRequest, sender: str) -> None:
        self.sender = sender
        self.setCreatedByUpdatedBy(request)

    def setReceiver(self, request: HttpRequest, receiver: str) -> None:
        self.receiver = receiver
        self.setCreatedByUpdatedBy(request)

    def setDate(self, request: HttpRequest, date: str) -> None:
        self.date = date
        self.setCreatedByUpdatedBy(request)
