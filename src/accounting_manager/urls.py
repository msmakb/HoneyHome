from django.urls import path
from . import views

urlpatterns = [
    path('Dashboard', views.Dashboard, name='AccountingManagerDashboard'),
    path('Sales', views.SalesPage, name='SalesPage'),
    path('Add-Sales', views.AddSalesPage, name='AddSalesPage'),
    path('Pricing', views.PricingPage, name='PricingPage'),
    path('Expenses', views.ExpensesPage, name='ExpensesPage'),
    path('Add-Expenses', views.AddExpensesPage, name='AddExpensesPage'),
    path('Update-Expense/<str:pk>', views.UpdateExpensePage, name='UpdateExpensePage'),
    path('Delete-Expense/<str:pk>', views.DeleteExpensePage, name='DeleteExpensePage'),
    path('Approve-Payments', views.ApprovePaymentsPage, name='ApprovePaymentsPage'),
    path('Approve-Payment/<str:pk>', views.ApprovePayment, name='ApprovePayment'),
]

