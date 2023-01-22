import logging
from typing import Any, Callable

from django.contrib import messages
from django.core.exceptions import EmptyResultSet
from django.db.models.functions import Lower
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.http.request import QueryDict
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from distributor.models import Distributor
from main import constants
from main import messages as MSG
from main.utils import Pagination
from main.utils import getUserBaseTemplate as base
from main.utils import resolvePageUrl, exportAsCsv

from .filters import GoodsMovementFilter
from .forms import (AddBatchForm, AddDamagedGoodsForm, AddGoodsForm, AddRetailGoodsForm,
                    ConvertToRetailForm, RegisterItemForm, SendGoodsForm)
from .models import (Batch, GoodsMovement, ItemCard, ItemType, RetailCard,
                     RetailItem, Stock)


# ----------------------------Dashboard------------------------------
def warehouseAdminDashboard(request: HttpRequest) -> HttpResponse:
    last_goods_movement: QuerySet[GoodsMovement] = GoodsMovement.getAllOrdered(
        'updated')[:3]

    context: dict[str, Any] = {'GoodsMovement': last_goods_movement}
    return render(request, constants.TEMPLATES.WAREHOUSE_ADMIN_DASHBOARD_TEMPLATE, context)


# --------------------------Main Storage-----------------------------
def MainStorageGoodsPage(request: HttpRequest) -> HttpResponse:
    item_cards: QuerySet[ItemCard] = ItemCard.orderFiltered(
        Lower('type__name'),
        stock__id=constants.MAIN_STORAGE_ID,
        status='Good',
        is_transforming=False
    )

    if request.method == constants.POST_METHOD:
        fields = ['type__name', 'type__code', 'batch__name',
                  'quantity', 'received_from', 'created']
        labels_to_change: dict[str, str] = {
            'type__name': 'item',
            'type__code': 'code',
            'batch__name': 'batch',
            'created': 'receiving date'
        }
        values_to_change: dict[str, Callable] = {
            'created': lambda date: timezone.datetime.strftime(date, '%d/%m/%Y')
        }
        file_name: str = "Main Storage Goods"
        try:
            response: HttpResponse = exportAsCsv(
                queryset=item_cards,
                fileName=file_name,
                fields=fields,
                labels_to_change=labels_to_change,
                values_to_change=values_to_change
            )
            return response
        except EmptyResultSet:
            messages.warning(request, "No data to export to the CSV file.")

    items_list: list[dict[str, str | int | list[str]]] = []
    # Below is a function to combine cards with same name
    for item in item_cards:
        for obj in items_list:
            if obj['type'] == item.type.name:
                obj['quantity'] += item.quantity
                for index, batch in enumerate(obj['batch']):
                    if batch[0] == item.batch.name:
                        obj['batch'][index][1] += item.quantity
                        break
                else:
                    obj['batch'].append([item.batch.name, item.quantity])
                break
        else:
            obj = {'type': item.type.name,
                   'batch': [[item.batch.name, item.quantity], ],
                   'quantity': item.quantity}
            items_list.append(obj)

    page: str = request.GET.get('page')
    pagination = Pagination(items_list, int(page) if page is not None else 1)
    page_obj: list[dict[str, Any]] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {'page_obj': page_obj, 'is_paginated': is_paginated,
                               'stock': constants.MAIN_STORAGE_ID, 'base': base(request)}
    return render(request, constants.TEMPLATES.MAIN_STORAGE_GOODS_TEMPLATE, context)


def DetailItemCardsPage(request: HttpRequest, pk: int, type: str) -> HttpResponse:
    Items: QuerySet[ItemCard] = ItemCard.orderFiltered(
        'updated',
        reverse=True,
        stock__id=pk,
        type__name=type,
        status=constants.ITEM_STATUS.GOOD,
        is_transforming=False
    )

    page: str = request.GET.get('page')
    pagination = Pagination(Items, int(page) if page is not None else 1)
    page_obj: QuerySet[ItemCard] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {'page_obj': page_obj, 'is_paginated': is_paginated,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.DETAIL_ITEM_CARD_TEMPLATE, context)


def AddGoodsPage(request: HttpRequest) -> HttpResponse:
    stock: Stock = Stock.get(id=constants.MAIN_STORAGE_ID)
    form = AddGoodsForm(request)
    if request.method == constants.POST_METHOD:
        updated_post: QueryDict = request.POST.copy()
        updated_post.update({'stock': stock})
        form = AddGoodsForm(request, updated_post)
        if form.is_valid():
            form_data: dict[str, Any] = form.cleaned_data
            type: ItemType = form_data.get('type')
            batch: Batch = form_data.get('batch')
            received_from: str = form_data.get('received_from')
            item_card: QuerySet[ItemCard] = ItemCard.filter(
                stock=constants.MAIN_STORAGE_ID,
                type=type,
                batch=batch,
                received_from=received_from,
                created__startswith=timezone.now().date())
            if item_card.exists():
                if len(item_card) == 1:
                    item_card: ItemCard = item_card[0]
                else:
                    item_card: ItemCard = ItemCard.orderFiltered(
                        'id', reverse=True, type=type, batch=batch,
                        received_from=received_from,
                        created__startswith=timezone.now().date())[0]
                quantity: int = int(form.cleaned_data.get('quantity'))
                item_card.setQuantity(request, item_card.quantity + quantity)
            else:
                form.save()

            return redirect(resolvePageUrl(request, constants.PAGES.MAIN_STORAGE_GOODS_PAGE))

    context: dict[str, Any] = {'form': form, 'base': base(request)}
    return render(request, constants.TEMPLATES.ADD_GOODS_TEMPLATE, context)


# --------------------------Registered Items--------------------------
def RegisteredItemsPage(request: HttpRequest) -> HttpResponse:
    item_types: QuerySet[ItemType] = ItemType.getAllOrdered(Lower('name'))

    if request.method == constants.POST_METHOD:
        fields = ['id', 'name', 'code', 'weight', 'is_retail']
        labels_to_change: dict[str, str] = {'id': 'item id'}
        values_to_change: dict[str, Callable] = {
            'is_retail': lambda is_retail: "Yes" if is_retail else "No"
        }
        file_name: str = "Registered Items"
        try:
            response: HttpResponse = exportAsCsv(
                queryset=item_types,
                fileName=file_name,
                fields=fields,
                labels_to_change=labels_to_change,
                values_to_change=values_to_change
            )
            return response
        except EmptyResultSet:
            messages.warning(request, "No data to export to the CSV file.")

    page: str = request.GET.get('page')
    pagination = Pagination(item_types, int(page) if page is not None else 1)
    page_obj: QuerySet[ItemCard] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context = {'page_obj': page_obj, 'is_paginated': is_paginated,
               'base': base(request)}
    return render(request, constants.TEMPLATES.REGISTERED_ITEMS_TEMPLATE, context)


def RegisterItemPage(request: HttpRequest) -> HttpResponse:
    form = RegisterItemForm(request)
    if request.method == constants.POST_METHOD:
        form = RegisterItemForm(request, request.POST)
        if form.is_valid():
            form.save()
            return redirect(resolvePageUrl(request, constants.PAGES.REGISTERED_ITEMS_PAGE))

    context: dict[str, Any] = {'form': form, 'base': base(request)}
    return render(request, constants.TEMPLATES.REGISTER_ITEM_TEMPLATE, context)


# -------------------------------Batches-------------------------------
def BatchesPage(request: HttpRequest) -> HttpResponse:
    Batches: QuerySet[Batch] = Batch.getAllOrdered(Lower('name'))

    if request.method == constants.POST_METHOD:
        fields = ['id', 'name', 'code', 'quantity',
                  'arrival_date', 'description']
        labels_to_change: dict[str, str] = {'id': 'batch id'}
        file_name: str = "Registered Batches"
        try:
            response: HttpResponse = exportAsCsv(
                queryset=Batches,
                fileName=file_name,
                fields=fields,
                labels_to_change=labels_to_change
            )
            return response
        except EmptyResultSet:
            messages.warning(request, "No data to export to the CSV file.")

    page: str = request.GET.get('page')
    pagination = Pagination(Batches, int(page) if page is not None else 1)
    page_obj: QuerySet[ItemCard] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {'page_obj': page_obj, 'is_paginated': is_paginated,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.BATCHES_TEMPLATE, context)


def AddBatchPage(request: HttpRequest) -> HttpResponse:
    form = AddBatchForm(request)
    if request.method == constants.POST_METHOD:
        form = AddBatchForm(request, request.POST)
        if form.is_valid():
            form.save()
            return redirect(resolvePageUrl(request, constants.PAGES.BATCHES_PAGE))

    context: dict[str, Any] = {'form': form, 'base': base(request)}
    return render(request, constants.TEMPLATES.ADD_BATCH_TEMPLATE, context)


# --------------------------Distributed Goods---------------------------
def DistributedGoodsPage(request: HttpRequest) -> HttpResponse:
    distributors: QuerySet[Distributor] = Distributor.getAllOrdered(
        Lower('person__name'))
    page: str = request.GET.get('page')
    pagination = Pagination(distributors, int(page) if page is not None else 1)
    page_obj: QuerySet[ItemCard] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context: dict[str, Any] = {'page_obj': page_obj, 'is_paginated': is_paginated,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.DISTRIBUTED_GOODS_TEMPLATE, context)


def DistributorStockPage(request: HttpRequest, pk: int) -> HttpResponse:
    item_cards: QuerySet[ItemCard] = ItemCard.orderFiltered(
        Lower('type__name'),
        stock__id=pk,
        status=constants.ITEM_STATUS.GOOD,
        is_transforming=False
    )

    if request.method == constants.POST_METHOD:
        fields = ['type__name', 'type__code', 'batch__name',
                  'quantity', 'received_from', 'created']
        labels_to_change: dict[str, str] = {
            'type__name': 'item',
            'type__code': 'code',
            'batch__name': 'batch',
            'created': 'receiving date'
        }
        values_to_change: dict[str, Callable] = {
            'created': lambda date: timezone.datetime.strftime(date, '%d/%m/%Y')
        }
        file_name: str = str(
            item_cards.first().stock) if item_cards.exists() else ""
        try:
            response: HttpResponse = exportAsCsv(
                queryset=item_cards,
                fileName=file_name,
                fields=fields,
                labels_to_change=labels_to_change,
                values_to_change=values_to_change
            )
            return response
        except EmptyResultSet:
            messages.warning(request, "No data to export to the CSV file.")

    items_list: list[dict] = []
    # Below is a function to combine cards with same name
    for item in item_cards:
        for obj in items_list:
            if obj['type'] == item.type.name:
                obj['quantity'] += item.quantity
                for index, batch in enumerate(obj['batch']):
                    if batch[0] == item.batch.name:
                        obj['batch'][index][1] += item.quantity
                        break
                else:
                    obj['batch'].append([item.batch.name, item.quantity])
                break
        else:
            obj = {'type': item.type.name,
                   'batch': [[item.batch.name, item.quantity], ],
                   'quantity': item.quantity}
            items_list.append(obj)

    page: str = request.GET.get('page')
    pagination = Pagination(items_list, int(page) if page is not None else 1)
    page_obj: list[dict] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated
    distributor: Distributor = Distributor.get(stock__id=pk)

    context: dict[str, Any] = {'page_obj': page_obj, 'is_paginated': is_paginated,
                               'distributor': distributor, 'base': base(request)}
    return render(request, 'warehouse_admin/distributor_stock.html', context)


def SendGoodsPage(request: HttpRequest, pk: int) -> HttpResponse:
    form = SendGoodsForm(request, constants.MAIN_STORAGE_ID)
    distributor: Distributor = Distributor.get(id=pk)
    if request.method == constants.POST_METHOD:
        form = SendGoodsForm(request, constants.MAIN_STORAGE_ID, request.POST)
        if form.is_valid():
            item_type: ItemType = form.cleaned_data.get('type')
            quantity: int = int(form.cleaned_data.get('quantity'))
            count: int = quantity
            batches: dict[Batch: int] = {}
            Items: QuerySet[ItemCard] = ItemCard.orderFiltered(
                'batch__created',
                stock=constants.MAIN_STORAGE_ID,
                type=item_type,
                status=constants.ITEM_STATUS.GOOD)
            while count != 0:
                if Items[0].quantity < count:
                    if Items[0].batch in batches:
                        batches[Items[0].batch] += Items[0].quantity
                    else:
                        batches[Items[0].batch] = Items[0].quantity
                    count -= Items[0].quantity
                    Items[0].delete(request)
                elif Items[0].quantity == count:
                    if Items[0].batch in batches:
                        batches[Items[0].batch] += Items[0].quantity
                    else:
                        batches[Items[0].batch] = Items[0].quantity
                    Items[0].delete(request)
                    break
                else:
                    if count > 0:
                        if Items[0].batch in batches:
                            batches[Items[0].batch] += count
                        else:
                            batches[Items[0].batch] = count
                        Items[0].setQuantity(
                            request, Items[0].quantity - count)
                    else:
                        if Items[0].batch in batches:
                            batches[Items[0].batch] += quantity
                        else:
                            batches[Items[0].batch] = quantity
                        Items[0].setQuantity(request, quantity)
                    break

            for batch, quantity in batches.items():
                print(batch, quantity)
                item_card: QuerySet[ItemCard] = ItemCard.filter(
                    stock=distributor.stock,
                    type=item_type,
                    batch=batch,
                    received_from=constants.MAIN_STORAGE_NAME,
                    created__startswith=timezone.now().date())
                if item_card.exists():
                    if len(item_card) == 1:
                        item_card: ItemCard = item_card[0]
                    else:
                        item_card: ItemCard = ItemCard.orderFiltered(
                            'id', reverse=True, type=item_type, batch=batch,
                            received_from=constants.MAIN_STORAGE_NAME,
                            stock=distributor.stock,
                            created__startswith=timezone.now().date())[0]
                    item_card.setQuantity(
                        request, item_card.quantity + quantity)
                else:
                    ItemCard.create(
                        request,
                        type=item_type, batch=batch,
                        stock=distributor.stock, quantity=quantity,
                        received_from=constants.MAIN_STORAGE_NAME)
                GoodsMovement.create(
                    request,
                    item=item_type.name,
                    code=item_type.code,
                    batch=str(batch),
                    quantity=quantity,
                    status=constants.ITEM_STATUS.GOOD,
                    sender=constants.MAIN_STORAGE_NAME,
                    receiver=distributor.person.name)

            return redirect(resolvePageUrl(request, constants.PAGES.DISTRIBUTOR_STOCK_PAGE), distributor.stock.id)

    context = {'form': form, 'distributor': distributor, 'base': base(request)}
    return render(request, constants.TEMPLATES.SEND_GOODS_TEMPLATE, context)


def GoodsMovementPage(request: HttpRequest) -> HttpResponse:
    queryset: QuerySet[GoodsMovement] = GoodsMovement.getAllOrdered(
        'created', reverse=True)
    goodsMovementFilter = GoodsMovementFilter(
        request.GET, queryset=queryset)
    queryset = goodsMovementFilter.qs

    if request.method == constants.POST_METHOD:
        fields = ['item', 'code', 'batch',
                  'quantity', 'sender',
                  'receiver', 'created', 'status']
        labels_to_change: dict[str, str] = {'created': 'Date'}
        values_to_change: dict[str, Callable] = {
            'created': lambda date: timezone.datetime.strftime(date, '%d/%m/%Y')
        }
        file_name: str = "Goods Movement History"
        try:
            response: HttpResponse = exportAsCsv(
                queryset=queryset,
                fileName=file_name,
                fields=fields,
                labels_to_change=labels_to_change,
                values_to_change=values_to_change
            )
            return response
        except EmptyResultSet:
            messages.warning(request, "No data to export to the CSV file.")

    page: str = request.GET.get('page')
    pagination = Pagination(goodsMovementFilter.qs, int(page)
                            if page is not None else 1)
    page_obj: QuerySet[ItemCard] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context = {'page_obj': page_obj, 'base': base(request), 'is_paginated': is_paginated,
               'goodsMovementFilter': goodsMovementFilter}
    return render(request, 'warehouse_admin/goods_movement.html', context)


def DamagedGoodsPage(request: HttpRequest) -> HttpResponse:
    MainStorageStock = Stock.objects.get(id=1)
    Items = ItemCard.objects.filter(
        stock=MainStorageStock, status='Damaged', is_transforming=False)
    context = {'Items': Items, 'base': base(
        request)}
    return render(request, 'warehouse_admin/damaged_goods.html', context)


def AddDamagedGoodsPage(request: HttpRequest) -> HttpResponse:
    form = AddDamagedGoodsForm(
        request, constants.MAIN_STORAGE_ID, show_batch=True)
    if request.method == constants.POST_METHOD:
        form = AddDamagedGoodsForm(
            request, constants.MAIN_STORAGE_ID, request.POST, show_batch=True)
        if form.is_valid():
            print("Valid Form")
            return redirect(resolvePageUrl(request, constants.PAGES.DAMAGED_GOODS_PAGE))
    # form = SendGoodsForm(request, 1)
    # availableItems = {}
    # Items = ItemCard.objects.filter(stock=1, status='Good')
    # for i in Items:
    #     availableItems[i.id] = {'name': i.type,
    #                             'batch': i.batch, 'quantity': i.quantity}
    # if request.method == "POST":
    #     form = SendGoodsForm(request, 1, request.POST)
    #     if form.is_valid:
    #         name = form['type'].value()
    #         batch = form['batch'].value()
    #         quantity = form['quantity'].value()
    #         received_from = form['received_from'].value()
    #         is_available = False
    #         for key, value in availableItems.items():
    #             if str(value['name']) == name and str(value['batch']) == batch and int(value['quantity']) >= int(quantity):
    #                 name = ItemType.objects.get(name=str(value['name']))
    #                 batch = Batch.objects.get(name=str(value['batch']))
    #                 is_available = True
    #                 if int(value['quantity']) == int(quantity):
    #                     ItemCard.objects.get(
    #                         type=name, batch=batch, stock=1, quantity=int(quantity)).delete()
    #                 else:
    #                     q = ItemCard.objects.get(
    #                         type=name, batch=batch, stock=1)
    #                     q.quantity = int(q.quantity - int(quantity))
    #                     q.save()

    #         if is_available:
    #             ItemCard.objects.create(type=ItemType.objects.get(name=name),
    #                                     batch=Batch.objects.get(
    #                                         name=str(batch)),
    #                                     stock=MainStorageStock,
    #                                     quantity=quantity,
    #                                     status='Damaged',
    #                                     received_from=received_from)
    #         else:
    #             messages.info(
    #                 request, "Item or quantity is not available in the stock")
    #             return redirect(resolvePageUrl(request, constants.PAGES.ADD_DAMAGED_GOODS_PAGE))
    #     return redirect(resolvePageUrl(request, constants.PAGES.DAMAGED_GOODS_PAGE))
    # context = {'availableItems': availableItems, 'form': form, 'base': base(
    #     request)}
    context: dict[str, Any] = {"form": form, "base": base(request)}
    return render(request, 'warehouse_admin/add_damaged_goods.html', context)


def transformedGoodsPage(request: HttpRequest) -> HttpResponse:
    items: QuerySet[ItemCard] = ItemCard.filter(is_transforming=True)

    if not items.exists():
        MSG.NO_TRANSFORMING(request)

    context: dict[str, Any] = {'Items': items,
                               'base': base(request)}
    return render(request, 'warehouse_admin/transformed_goods.html', context)


def approveTransformingGoods(request: HttpRequest, pk: int) -> HttpResponseRedirect:
    item: ItemCard = get_object_or_404(ItemCard, id=pk)
    if not item.is_transforming:
        raise Http404

    MSG.APPROVED_TRANSFORMING(request, item)
    stock: Stock = Stock.get(id=item.transforming_to_stock)
    distributer: Distributor = item.stock.getStockOwner()
    item.setStock(request, stock)
    item.setReceivedFrom(request, distributer.person.name)
    item.setPriced(request, False)
    item.setPrice(request, None)
    item.setTransforming(request, False)
    item.setTransformingToStock(request, 0)

    return redirect(resolvePageUrl(request, constants.PAGES.TRANSFORMED_GOODS_PAGE))


def declineTransformingGoods(request: HttpRequest, pk: int) -> HttpResponseRedirect:
    item: ItemCard = get_object_or_404(ItemCard, id=pk)
    if not item.is_transforming:
        raise Http404

    MSG.DECLINED_TRANSFORMING(request, item)
    item.setTransforming(request, False)
    item.setTransformingToStock(request, 0)

    return redirect(resolvePageUrl(request, constants.PAGES.TRANSFORMED_GOODS_PAGE))


def RetailGoodsPage(request: HttpRequest) -> HttpResponse:
    retailCard = RetailCard.objects.all()
    retailItem = RetailItem.objects.all()
    context = {'retailItem': retailItem, 'retailCard': retailCard, 'base': base(
        request)}
    return render(request, 'warehouse_admin/retail_goods.html', context)


def ConvertToRetailPage(request: HttpRequest) -> HttpResponse:
    form = ConvertToRetailForm()
    availableItems = {}
    Items = ItemCard.objects.filter(stock=1, status="Good")
    for i in Items:
        availableItems[i.id] = {'name': i.type,
                                'batch': i.batch, 'quantity': i.quantity}
    if request.method == "POST":
        form = ConvertToRetailForm(request.POST)
        if form.is_valid:
            name = form['type'].value()
            batch = form['batch'].value()
            quantity = form['quantity'].value()
            is_available = False
            for key, value in availableItems.items():
                if str(value['name']) == name and str(value['batch']) == batch and int(value['quantity']) >= int(quantity):
                    name = ItemType.objects.get(name=str(value['name']))
                    batch = Batch.objects.get(name=str(value['batch']))
                    is_available = True
                    if int(value['quantity']) == int(quantity):
                        ItemCard.objects.get(
                            type=name, batch=batch, status="Good", stock=1, quantity=int(quantity)).delete()
                    else:
                        q = ItemCard.objects.get(
                            type=name, batch=batch, status="Good", stock=1)
                        q.quantity = int(q.quantity - int(quantity))
                        q.save()

            if is_available:
                RetailCard.objects.create(type=ItemType.objects.get(
                    name=name), weight=int(quantity) * 7000)
            else:
                messages.info(
                    request, "Item or quantity is not available in the stock")
                return redirect('ConvertToRetailPage')
        return redirect(resolvePageUrl(request, constants.PAGES.RETAIL_GOODS_PAGE))

    context = {'availableItems': availableItems, 'form': form, 'base': base(
        request)}
    return render(request, 'warehouse_admin/convert_to_retail.html', context)


def AddRetailGoodsPage(request: HttpRequest) -> HttpResponse:
    form = AddRetailGoodsForm()
    if request.method == "POST":
        form = AddRetailGoodsForm(request.POST)
        if form.is_valid():
            stock = RetailItem.objects.all()
            name = form['type'].value()
            Type = ItemType.objects.get(name=str(name))
            quantity = form['quantity'].value()
            is_available = False
            for item in stock:
                if item.type == Type:
                    is_available = True
            if is_available:
                q = RetailItem.objects.get(type=Type)
                q.quantity = int(q.quantity + int(quantity))
                q.save()
            else:
                RetailItem.objects.create(type=Type, quantity=quantity)
            q = RetailCard.objects.all()[0]
            q.weight = int(
                q.weight) - int(RetailItem.objects.all().order_by('-id')[0].type.weight)
            q.save()
        return redirect(resolvePageUrl(request, constants.PAGES.RETAIL_GOODS_PAGE))

    context = {'form': form, 'base': base(
        request)}
    return render(request, 'warehouse_admin/add_retail_goods.html', context)
