from typing import Any, Callable

from django.core.exceptions import EmptyResultSet
from django.db.models.functions import Lower
from django.db.models.query import QuerySet, Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.http.request import QueryDict
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.timezone import timedelta

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
                     RetailItem, Stock, DamagedGoodsHistory)


# ----------------------------Dashboard------------------------------
def warehouseAdminDashboard(request: HttpRequest) -> HttpResponse:
    main_storage_goods: int = 0
    distributed_goods: int = 0
    retail_goods: int = 0
    total_goods: int = 0
    damaged_goods: int = 0
    converted_retail: int = RetailCard.countAll()
    awaiting_approval_goods: int = ItemCard.countFiltered(is_transforming=True)
    monthly_movement_goods: int = GoodsMovement.countFiltered(
        created__gte=timezone.now() - timedelta(days=30))
    distributors: int = Distributor.countAll()
    batches: int = Batch.countAll()
    registered_retail_items: int = ItemType.countFiltered(is_retail=True)
    registered_items: int = ItemType.countAll()
    for item in ItemCard.filter(stock__id=constants.MAIN_STORAGE_ID):
        if item.status == constants.ITEM_STATUS.DAMAGED:
            damaged_goods += item.quantity
        main_storage_goods += item.quantity
        total_goods += item.quantity
    for item in RetailItem.getAll():
        main_storage_goods += item.quantity
        retail_goods += item.quantity
        total_goods += item.quantity
    for item in ItemCard.filter(~Q(stock__id=constants.MAIN_STORAGE_ID)):
        distributed_goods += item.quantity
        total_goods += item.quantity

    last_goods_movement: QuerySet[GoodsMovement] = GoodsMovement.getAllOrdered(
        'updated')[:3]

    context: dict[str, Any] = {
        'MainStorageGoods': main_storage_goods,
        'DistributedGoods': distributed_goods,
        'RetailGoods': retail_goods,
        'TotalGoods': total_goods,
        'DamagedGoods': damaged_goods,
        'ConvertedRetail': converted_retail,
        'AwaitingApprovalGoods': awaiting_approval_goods,
        'MonthlyMovementGoods': monthly_movement_goods,
        'Distributors': distributors,
        'Batches': batches,
        'RegisteredRetailItems': registered_retail_items,
        'RegisteredItems': registered_items,
        'GoodsMovement': last_goods_movement
    }
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
            MSG.EMPTY_RESULT(request)

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
            data: tuple[str, int] = form.save()
            MSG.ITEM_ADDED(request, data[0], data[1])

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
            MSG.EMPTY_RESULT(request)

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
            MSG.ITEM_REGISTERED(request)
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
            MSG.EMPTY_RESULT(request)

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
        print(form.errors)
        if form.is_valid():
            form.save()
            MSG.BATCH_REGISTERED(request)
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
            MSG.EMPTY_RESULT(request)

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
    return render(request, constants.TEMPLATES.DISTRIBUTOR_STOCK_TEMPLATE, context)


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
            MSG.STOCK_UPDATED(request)

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
            MSG.EMPTY_RESULT(request)

    page: str = request.GET.get('page')
    pagination = Pagination(goodsMovementFilter.qs, int(page)
                            if page is not None else 1)
    page_obj: QuerySet[ItemCard] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context = {'page_obj': page_obj, 'base': base(request), 'is_paginated': is_paginated,
               'goodsMovementFilter': goodsMovementFilter}
    return render(request, constants.TEMPLATES.GOODS_MOVEMENT_TEMPLATE, context)


def DamagedGoodsPage(request: HttpRequest) -> HttpResponse:
    item_cards = ItemCard.orderFiltered(
        'created',
        reverse=True,
        stock__id=constants.MAIN_STORAGE_ID,
        status=constants.ITEM_STATUS.DAMAGED,
        is_transforming=False
    )

    page: str = request.GET.get('page')
    pagination = Pagination(item_cards, int(page) if page is not None else 1)
    page_obj: QuerySet[ItemCard] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context = {'page_obj': page_obj, 'is_paginated': is_paginated,
               'base': base(request)}
    return render(request, constants.TEMPLATES.DAMAGED_GOODS_TEMPLATE, context)


def damagedGoodsHistoryPage(request: HttpRequest) -> HttpResponse:
    damaged_goods_history: DamagedGoodsHistory = DamagedGoodsHistory.getAllOrdered(
        'created',
        reverse=True
    )

    if request.method == constants.POST_METHOD:
        fields = ['item', 'batch', 'quantity', 'received_from',
                  'created', 'description']
        labels_to_change: dict[str, str] = {
            'item': 'item',
            'batch': 'batch',
            'created': 'date'
        }
        values_to_change: dict[str, Callable] = {
            'created': lambda date: timezone.datetime.strftime(date, '%d/%m/%Y')
        }
        file_name: str = "Damaged Goods History"
        try:
            response: HttpResponse = exportAsCsv(
                queryset=damaged_goods_history,
                fileName=file_name,
                fields=fields,
                labels_to_change=labels_to_change,
                values_to_change=values_to_change
            )
            return response
        except EmptyResultSet:
            MSG.EMPTY_RESULT(request)

    page: str = request.GET.get('page')
    pagination = Pagination(damaged_goods_history, int(
        page) if page is not None else 1)
    page_obj: QuerySet[ItemCard] = pagination.getPageObject()
    is_paginated: bool = pagination.isPaginated

    context = {'page_obj': page_obj, 'is_paginated': is_paginated,
               'base': base(request)}
    return render(request, constants.TEMPLATES.DAMAGED_GOODS_History_TEMPLATE, context)


def AddDamagedGoodsPage(request: HttpRequest) -> HttpResponse:
    form = AddDamagedGoodsForm(request)
    if request.method == constants.POST_METHOD:
        form = AddDamagedGoodsForm(request, request.POST)
        if form.is_valid():
            cleaned_data: dict[str, Any] = form.cleaned_data
            item_type: ItemType = cleaned_data.get('type')
            batch: Batch = cleaned_data.get('batch')
            received_from: str = cleaned_data.get('received_from')
            quantity: int = int(cleaned_data.get('quantity'))
            note: str = cleaned_data.get('note')
            count: int = quantity
            items: QuerySet[ItemCard] = ItemCard.orderFiltered(
                'created',
                reverse=True,
                stock__id=constants.MAIN_STORAGE_ID,
                type=item_type,
                batch=batch,
                status=constants.ITEM_STATUS.GOOD)

            while count != 0:
                if items[0].quantity < count:
                    count -= items[0].quantity
                    items[0].delete(request)
                elif items[0].quantity == count:
                    items[0].delete(request)
                    break
                else:
                    items[0].setQuantity(request, items[0].quantity - count)
                    break

            item_card: QuerySet[ItemCard] = ItemCard.filter(
                stock__id=constants.MAIN_STORAGE_ID,
                status=constants.ITEM_STATUS.DAMAGED,
                type=item_type,
                batch=batch,
                received_from=received_from,
                note=note,
                created__startswith=timezone.now().date()
            )

            if item_card.exists():
                item_card[0].setQuantity(
                    request, item_card[0].quantity + quantity)
            else:
                ItemCard.create(
                    request,
                    stock=Stock.get(id=constants.MAIN_STORAGE_ID),
                    status=constants.ITEM_STATUS.DAMAGED,
                    type=item_type,
                    batch=batch,
                    received_from=received_from,
                    note=note,
                    quantity=quantity,
                )

            DamagedGoodsHistory.create(
                request,
                item=item_type.name,
                batch=batch.name,
                quantity=quantity,
                received_from=received_from,
                description=note
            )
            MSG.DAMAGED_GOODS_ADDED(request)

            return redirect(resolvePageUrl(request, constants.PAGES.DAMAGED_GOODS_PAGE))

    context: dict[str, Any] = {"form": form, "base": base(request)}
    return render(request, constants.TEMPLATES.ADD_DAMAGED_GOODS_TEMPLATE, context)


def transformedGoodsPage(request: HttpRequest) -> HttpResponse:
    items: QuerySet[ItemCard] = ItemCard.filter(is_transforming=True)

    if not items.exists():
        MSG.NO_TRANSFORMING(request)

    context: dict[str, Any] = {'Items': items,
                               'base': base(request)}
    return render(request, constants.TEMPLATES.TRANSFORMED_GOODS_TEMPLATE, context)


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


def RetailGoodsPage(request: HttpRequest, currentPage: str) -> HttpResponse:
    context = {'currentPage': currentPage, 'base': base(request)}

    match currentPage:
        case "Retail-Goods":
            retail_items = RetailItem.objects.all()
            page: str = request.GET.get('page')
            pagination = Pagination(retail_items, int(
                page) if page is not None else 1)
            page_obj: QuerySet[ItemCard] = pagination.getPageObject()
            is_paginated: bool = pagination.isPaginated

            context['page_obj'] = page_obj
            context['is_paginated'] = is_paginated
        case "Converted-Retail":
            retail_cards = RetailCard.objects.all()
            page: str = request.GET.get('page')
            pagination = Pagination(retail_cards, int(
                page) if page is not None else 1)
            page_obj: QuerySet[ItemCard] = pagination.getPageObject()
            is_paginated: bool = pagination.isPaginated

            context['page_obj'] = page_obj
            context['is_paginated'] = is_paginated
        case "Add-Retail":
            form = AddRetailGoodsForm(request)
            if request.method == constants.POST_METHOD:
                form = AddRetailGoodsForm(request, request.POST)
                if form.is_valid():
                    cleaned_data: dict[str, Any] = form.cleaned_data
                    item_type: ItemType = cleaned_data.get('type')
                    quantity: int = cleaned_data.get('quantity')
                    form.save()
                    MSG.ITEM_ADDED(request, item_type.name, quantity)

                    return redirect(resolvePageUrl(request, constants.PAGES.RETAIL_GOODS_PAGE), 'Retail-Goods')

            context['form'] = form
        case "Convert-Retail":
            form = ConvertToRetailForm(request)
            if request.method == constants.POST_METHOD:
                form = ConvertToRetailForm(request, request.POST)
                if form.is_valid():
                    cleaned_data: dict[str, Any] = form.cleaned_data
                    from_type: ItemType = ItemType.get(
                        name=cleaned_data.get("from_type"))
                    to_type: ItemType = ItemType.get(
                        name=cleaned_data.get("type"))
                    quantity: int = int(cleaned_data.get("quantity"))
                    weight: int = int(cleaned_data.get("weight"))
                    count: int = quantity

                    items: QuerySet[ItemCard] = ItemCard.orderFiltered(
                        'status',
                        stock__id=constants.MAIN_STORAGE_ID,
                        type=from_type)

                    while count != 0:
                        if items[0].quantity < count:
                            count -= items[0].quantity
                            items[0].delete(request)
                        elif items[0].quantity == count:
                            items[0].delete(request)
                            break
                        else:
                            items[0].setQuantity(
                                request, items[0].quantity - count)
                            break

                    if int(weight):
                        MSG.CONVERTED_SUCCESSFULLY(
                            request, from_type.name, to_type.name)
                    else:
                        MSG.DAMAGED_GOODS_DELETED(request)

                    form.save()
                    return redirect(resolvePageUrl(request, constants.PAGES.RETAIL_GOODS_PAGE), 'Converted-Retail')

            context['form'] = form
        case _:
            Http404

    return render(request, constants.TEMPLATES.RETAIL_GOODS_TEMPLATE, context)
