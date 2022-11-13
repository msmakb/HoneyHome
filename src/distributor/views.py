from django.shortcuts import render, redirect
from django.contrib import messages
#from django.core.files.storage import FileSystemStorage
from main.models import Person
from main.utils import resolvePageUrl
from main import constants
from warehouse_admin.forms import SendGoodsForm
from warehouse_admin.models import Batch, Stock, ItemType, ItemCard, GoodsMovement
from .forms import SendPaymentForm
from .models import Distributor, SalesHistory


def Dashboard(request):
    dis = Distributor.objects.get(account=request.user)
    sales = SalesHistory.objects.filter(distributor=dis)

    context = {'sales': sales}
    return render(request, 'distributor/dashboard.html', context)


def GoodsPage(request):
    distributor = Distributor.objects.get(account=request.user)
    stock = ItemCard.objects.filter(
        stock=distributor.stock, is_priced=True, is_transforming=False)

    context = {'Items': stock}
    return render(request, 'distributor/goods.html', context)


def SendPaymentPage(request):
    dis = Distributor.objects.get(account=request.user)
    stock = dis.stock.id
    form = SendPaymentForm(stock)
    availableItems = {}
    Items = ItemCard.objects.filter(stock=stock, status='Good')
    for i in Items:
        availableItems[i.id] = {'name': i.type,
                                'batch': i.batch, 'quantity': i.quantity}
    if request.method == "POST":
        form = SendPaymentForm(stock, request.POST)
        receipt = request.FILES['receipt']
        print(receipt.name)
        #fs = FileSystemStorage("media/receipts")
        #fs.save(receipt.name, receipt)

    context = {'availableItems': availableItems, 'form': form}
    return render(request, 'distributor/send_payment.html', context)


def FreezeItemPage(request):
    distributor = Distributor.objects.get(account=request.user)
    stock = int(distributor.stock.id)
    form = SendGoodsForm(stock)
    availableItems = {}
    Items = ItemCard.objects.filter(stock=stock, status='Good')
    Item = None
    for i in Items:
        availableItems[i.id] = {'name': i.type,
                                'batch': i.batch, 'quantity': i.quantity}
    if request.method == "POST":
        form = SendGoodsForm(stock, request.POST)
        if form.is_valid:
            name = form['type'].value()
            batch = form['batch'].value()
            quantity = form['quantity'].value()
            is_available = False
            for key, value in availableItems.items():
                if str(value['name']) == name and str(value['batch']) == batch and int(value['quantity']) >= int(quantity):
                    name = ItemType.objects.get(name=str(value['name']))
                    batch = Batch.objects.get(name=str(value['batch']))
                    Item = ItemCard.objects.filter(type=name, batch=batch)[0]
                    is_available = True
                    if int(value['quantity']) == int(quantity):
                        ItemCard.objects.get(type=name, batch=batch, stock=stock, quantity=int(
                            quantity), status="Good").delete()
                        Item = ItemCard.objects.filter(
                            type=name, batch=batch, quantity=int(quantity))[0]
                    else:
                        q = ItemCard.objects.filter(
                            type=name, batch=batch, stock=stock, status="Good")[0]
                        q.quantity = int(q.quantity - int(quantity))
                        q.save()

            if is_available:
                ItemCard.objects.create(type=ItemType.objects.get(name=name),
                                        batch=Batch.objects.get(
                                            name=str(batch)),
                                        stock=Stock.objects.get(id=stock),
                                        quantity=quantity,
                                        status='Frozen',
                                        received_from=Item.received_from,
                                        is_transforming=False)

            else:
                messages.info(
                    request, "Item or quantity is not available in the stock")
                return redirect(resolvePageUrl(request, constants.PAGES.RETURN_ITEMS_PAGE))
        messages.success(request, f"Item has been successfully Frozen")
        return redirect(resolvePageUrl(request, constants.PAGES.RETURN_ITEMS_PAGE))
    context = {'availableItems': availableItems, 'form': form}
    return render(request, 'distributor/freeze_item.html', context)


def ReturnItemPage(request):
    distributor = Distributor.objects.get(account=request.user)
    stock = int(distributor.stock.id)
    form = SendGoodsForm(stock)
    availableItems = {}
    receiver_name = 'Main Storage'
    Items = ItemCard.objects.filter(stock=stock, status='Good')
    for i in Items:
        availableItems[i.id] = {'name': i.type,
                                'batch': i.batch, 'quantity': i.quantity}
    if request.method == "POST":
        form = SendGoodsForm(stock, request.POST)
        if form.is_valid:
            name = form['type'].value()
            batch = form['batch'].value()
            quantity = form['quantity'].value()
            status = form['status'].value()
            receiver = form['send_to'].value()
            is_available = False
            for key, value in availableItems.items():
                if str(value['name']) == name and str(value['batch']) == batch and int(value['quantity']) >= int(quantity):
                    name = ItemType.objects.get(name=str(value['name']))
                    batch = Batch.objects.get(name=str(value['batch']))
                    is_available = True
                    if int(value['quantity']) == int(quantity):
                        ItemCard.objects.get(type=name, batch=batch, stock=stock, quantity=int(
                            quantity), status="Good").delete()
                    else:
                        q = ItemCard.objects.filter(
                            type=name, batch=batch, stock=stock, status="Good")[0]
                        q.quantity = int(q.quantity - int(quantity))
                        q.save()

            if is_available:
                if receiver == "Main Storage":
                    receiver = 1
                else:
                    person = Person.objects.get(name=str(receiver))
                    dis = Distributor.objects.get(person=person)
                    receiver = dis.stock.id
                    receiver_name = dis.person.name
                stock = Stock.objects.get(id=receiver)
                ItemCard.objects.create(type=ItemType.objects.get(name=name),
                                        batch=Batch.objects.get(
                                            name=str(batch)),
                                        stock=stock,
                                        quantity=quantity,
                                        status=status,
                                        received_from=distributor.person.name,
                                        is_transforming=True)
                GoodsMovement.objects.create(item=ItemCard.objects.all().order_by('-id')[0],
                                             sender=Distributor.objects.get(
                                                 account=request.user).person.name,
                                             receiver=str(receiver_name))
            else:
                messages.info(
                    request, "Item or quantity is not available in the stock")
                return redirect(resolvePageUrl(request, constants.PAGES.RETURN_ITEMS_PAGE))
        messages.success(
            request, f"Item has been successfully sended to {receiver_name}")
        return redirect(resolvePageUrl(request, constants.PAGES.RETURN_ITEMS_PAGE))
    context = {'availableItems': availableItems, 'form': form}
    return render(request, 'distributor/return_item.html', context)


def HistoryPage(request):
    dis = Distributor.objects.get(account=request.user)
    sales = SalesHistory.objects.filter(distributor=dis)

    context = {'Sales': sales}
    return render(request, 'distributor/history.html', context)
