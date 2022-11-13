from django.urls import path

from main.constants import PAGES

from . import views


app_name = 'accounting_manager'
urlpatterns = [
    path(
        f'{PAGES.DASHBOARD}/',
        views.Dashboard,
        name=PAGES.ACCOUNTING_MANAGER_DASHBOARD
    ),
    path(
        f'{PAGES.DASHBOARD}/Sales/',
        views.SalesPage,
        name=PAGES.SALES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Add-Sales/',
        views.AddSalesPage,
        name=PAGES.ADD_SALES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Pricing/',
        views.PricingPage,
        name=PAGES.PRICING_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Expenses/',
        views.ExpensesPage,
        name=PAGES.EXPENSES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Add-Expenses/',
        views.AddExpensesPage,
        name=PAGES.ADD_EXPENSES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Update-Expense/<str:pk>/',
        views.UpdateExpensePage,
        name=PAGES.UPDATE_EXPENSES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Delete-Expense/<str:pk>/',
        views.DeleteExpensePage,
        name=PAGES.DELETE_EXPENSES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Approve-Payments/',
        views.ApprovePaymentsPage,
        name=PAGES.APPROVE_PAYMENTS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Approve-Payment/<str:pk>/',
        views.ApprovePayment,
        name=PAGES.APPROVE_PAYMENT_PAGE
    ),
]
