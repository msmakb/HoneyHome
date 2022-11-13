from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from main import constants
from main.utils import getEmployeesTasks as EmployeeTasks
from main.utils import getUserBaseTemplate as base
from main.utils import resolvePageUrl
from warehouse_admin.models import ItemCard, RetailItem
from .filters import SalesFilter
from .forms import AddExpensesForm, AddSalesForm
from .models import Expenses, Sales


def Dashboard(request):
    sales = Sales.objects.filter(is_approved=True).order_by('-id')[:5]

    context = {'Sales': sales, 'EmployeeTasks': EmployeeTasks(request)}
    return render(request, 'accounting_manager/dashboard.html', context)


def SalesPage(request):
    sales = Sales.objects.filter(is_approved=True)
    filter = SalesFilter(request.GET, sales)
    sales = filter.qs

    context = {'SalesFilter': filter, 'Sales': sales, 'base': base(
        request), 'EmployeeTasks': EmployeeTasks(request)}
    return render(request, 'accounting_manager/sales.html', context)


def AddSalesPage(request):
    form = AddSalesForm()
    availableItems = {}
    Items = ItemCard.objects.filter(stock=1, status='Good')
    for i in Items:
        availableItems[i.id] = {'name': i.type,
                                'batch': i.batch, 'quantity': i.quantity}
    Items = RetailItem.objects.all()
    for i in Items:
        availableItems[i.id] = {'name': i.type,
                                'batch': None, 'quantity': i.quantity}
    if request.method == "POST":
        form = AddSalesForm(request.POST)
        if form.is_valid():
            form.save()
        sale = Sales.objects.all().order_by('-id')[0]
        sale.seller = 'Main Storage'
        sale.is_approved = True
        sale.save()

        return redirect(resolvePageUrl(request, constants.PAGES.SALES_PAGE))

    context = {'form': form, 'availableItems': availableItems,
               'base': base(request), 'EmployeeTasks': EmployeeTasks(request)}
    return render(request, 'accounting_manager/add_sales.html', context)


def PricingPage(request):
    unpricedGoods = ItemCard.objects.filter(~Q(stock=1), is_priced=False)
    if request.method == "POST":
        id = request.POST.get('id', False)
        val = request.POST.get(f'val{str(id)}', False)
        item = ItemCard.objects.get(id=int(id))
        price = int(val)
        item.price = price
        item.is_priced = True
        item.save()

        if not ItemCard.objects.filter(~Q(stock=1), is_priced=False).exists():
            messages.info(request, "There is no more goods to be priced")
            from main.models import Task
            task = Task.objects.get(id=12)
            task.is_rated = True
            task.status = "On-Time"
            task.save()
        messages.success(
            request, f"The item '{item.type}' sent from '{item.received_from}' to '{item.getReceiver()}' has been priced by '{item.price}IDR' for evry item of '{item.quantity}' totaled '{item.getTotal()}IDR'")

    context = {'UnpricedGoods': unpricedGoods, 'base': base(
        request), 'EmployeeTasks': EmployeeTasks(request)}
    return render(request, 'accounting_manager/pricing.html', context)


def ExpensesPage(request):
    expenses = Expenses.objects.all()
    from django import template

    register = template.Library()

    @register.filter
    def multiply(value, arg):
        return value * arg

    context = {'multiply': multiply, 'Expenses': expenses,
               'base': base(request), 'EmployeeTasks': EmployeeTasks(request)}
    return render(request, 'accounting_manager/expenses.html', context)


def AddExpensesPage(request):
    form = AddExpensesForm()
    if request.method == "POST":
        form = AddExpensesForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(resolvePageUrl(request, constants.PAGES.EXPENSES_PAGE))

    context = {'form': form, 'base': base(
        request), 'EmployeeTasks': EmployeeTasks(request)}
    return render(request, 'accounting_manager/add_expenses.html', context)


def UpdateExpensePage(request, pk):
    expenses = Expenses.objects.get(id=pk)
    form = AddExpensesForm(instance=expenses)
    if request.method == 'POST':
        form = AddExpensesForm(request.POST, instance=expenses)
        if form.is_valid():
            form.save()

        return redirect(resolvePageUrl(request, constants.PAGES.EXPENSES_PAGE))

    context = {'form': form, 'base': base(
        request), 'EmployeeTasks': EmployeeTasks(request)}
    return render(request, 'accounting_manager/update_expense.html', context)


def DeleteExpensePage(request, pk):
    Expense = Expenses.objects.get(id=pk)
    if request.method == "POST":
        Expense.delete()

        return redirect(resolvePageUrl(request, constants.PAGES.EXPENSES_PAGE))

    context = {'Expense': Expense, 'base': base(
        request), 'EmployeeTasks': EmployeeTasks(request)}
    return render(request, 'accounting_manager/delete-expensePage.html', context)


def ApprovePaymentsPage(request):
    sales = Sales.objects.filter(is_approved=False)

    context = {'Sales': sales, 'base': base(
        request), 'EmployeeTasks': EmployeeTasks(request)}
    return render(request, 'accounting_manager/approve_payments.html', context)


def ApprovePayment(request, pk):
    sale = Sales.objects.get(id=pk)
    sale.is_approved = True
    sale.save()

    if not Sales.objects.filter(is_approved=False).exists():
        messages.info(request, "There is no payments to be approved")
        from main.models import Task
        task = Task.objects.get(id=11)
        task.is_rated = True
        task.status = "On-Time"
        task.save()
    messages.success(
        request, f"The Payment sent from '{sale.seller}' for '{sale.type} - {sale.batch} ({sale.quantity}): {sale.price}IDR' has been 'approved'")

    return redirect(resolvePageUrl(request, constants.PAGES.APPROVE_PAYMENTS_PAGE))
