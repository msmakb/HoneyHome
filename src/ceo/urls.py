from django.urls import path
from main.constants import PAGES
from . import views as ceo_views
from accounting_manager import views as am_views
from human_resources import views as hr_views
from warehouse_admin import views as wa_views

app_name = "ceo"
urlpatterns = [
    path(
        f'{PAGES.DASHBOARD}/',
        ceo_views.Dashboard,
        name=PAGES.CEO_DASHBOARD
    ),
    # Employees URLs
    path(
        f'{PAGES.DASHBOARD}/Employees/',
        hr_views.employeesPage,
        name=PAGES.EMPLOYEES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Employee/Add-Employee/',
        hr_views.addEmployeePage,
        name=PAGES.ADD_EMPLOYEE_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Employee/<str:pk>/',
        hr_views.employeePage,
        name=PAGES.EMPLOYEE_RECORD_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Employee/Update/<str:pk>/',
        hr_views.updateEmployeePage,
        name=PAGES.UPDATE_EMPLOYEE_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Employee/Delete/<str:pk>/',
        hr_views.deleteEmployeePage,
        name=PAGES.DELETE_EMPLOYEE_PAGE
    ),
    # Distributors URLs
    path(
        f'{PAGES.DASHBOARD}/Distributors/',
        hr_views.distributorsPage,
        name=PAGES.DISTRIBUTORS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor/Add-Distributor/',
        hr_views.addDistributorPage,
        name=PAGES.ADD_DISTRIBUTOR_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor/<str:pk>/',
        hr_views.distributorPage,
        name=PAGES.DISTRIBUTOR_RECORD_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor/Update/<str:pk>/',
        hr_views.updateDistributorPage,
        name=PAGES.UPDATE_DISTRIBUTOR_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor/Delete/<str:pk>/',
        hr_views.deleteDistributorPage,
        name=PAGES.DELETE_DISTRIBUTOR_PAGE
    ),
    # Tasks URLs
    path(
        f'{PAGES.DASHBOARD}/Tasks/',
        hr_views.employeeTasksPage,
        name=PAGES.EMPLOYEES_TASKS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Task/Add-Task/',
        hr_views.addTaskPage,
        name=PAGES.ADD_TASK_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Task/<str:pk>/',
        hr_views.taskPage,
        name=PAGES.DETAILED_TASK_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Task/Update/<str:pk>/',
        hr_views.updateTaskPage,
        name=PAGES.UPDATE_TASK_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Task/Delete/<str:pk>/',
        hr_views.deleteTaskPage,
        name=PAGES.DELETE_TASK_PAGE
    ),
    # Evaluation URLs
    path(
        f'{PAGES.DASHBOARD}/Evaluation/',
        hr_views.evaluationPage,
        name=PAGES.EVALUATION_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Weekly-Evaluation/',
        hr_views.weeklyEvaluationPage,
        name=PAGES.WEEKLY_EVALUATION_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Task-Evaluation/',
        hr_views.taskEvaluationPage,
        name=PAGES.TASK_EVALUATION_PAGE
    ),
    # --------------------------Main Storage URLs-----------------------------
    path(
        f'{PAGES.DASHBOARD}/Main-Storage/',
        wa_views.MainStorageGoodsPage,
        name=PAGES.MAIN_STORAGE_GOODS_PAGE,
    ),
    path(
        f'{PAGES.DASHBOARD}/Detailed-Item-Cards/<str:pk>/<str:type>/',
        wa_views.DetailItemCardsPage,
        name=PAGES.DETAIL_ITEM_CARDS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Add-Goods/',
        wa_views.AddGoodsPage,
        name=PAGES.ADD_GOODS_PAGE
    ),

    # -------------------------RegisteredItems URLs---------------------------
    path(
        f'{PAGES.DASHBOARD}/Registered-Items/',
        wa_views.RegisteredItemsPage,
        name=PAGES.REGISTERED_ITEMS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Register-Item/',
        wa_views.RegisterItemPage,
        name=PAGES.REGISTER_NEW_ITEM_PAGE
    ),

    # Batches URLs
    path(
        f'{PAGES.DASHBOARD}/Batches/',
        wa_views.BatchesPage,
        name=PAGES.BATCHES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Add-Batch/',
        wa_views.AddBatchPage,
        name=PAGES.ADD_BATCH_PAGE
    ),
    # Distributed Goods URLs
    path(
        f'{PAGES.DASHBOARD}/Distributed-Goods/',
        wa_views.DistributedGoodsPage,
        name=PAGES.DISTRIBUTED_GOODS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor-Stock/<str:pk>',
        wa_views.DistributorStockPage,
        name=PAGES.DISTRIBUTOR_STOCK_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Send-Goods/<str:pk>/',
        wa_views.SendGoodsPage,
        name=PAGES.SEND_GOODS_PAGE
    ),
    # Goods Movement URLs
    path(
        f'{PAGES.DASHBOARD}/Goods-Movement/',
        wa_views.GoodsMovementPage,
        name=PAGES.GOODS_MOVEMENT_PAGE
    ),
    # Damaged Goods URLs
    path(
        f'{PAGES.DASHBOARD}/Damaged-Goods/',
        wa_views.DamagedGoodsPage,
        name=PAGES.DAMAGED_GOODS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Add-Damaged-Goods/',
        wa_views.AddDamagedGoodsPage,
        name=PAGES.ADD_DAMAGED_GOODS_PAGE
    ),
    # Transformed Goods URLs
    path(
        f'{PAGES.DASHBOARD}/Transformed-Goods/',
        wa_views.TransformedGoodsPage,
        name=PAGES.TRANSFORMED_GOODS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Approve-Transformed/<str:pk>/',
        wa_views.ApproveTransformedGoods,
        name=PAGES.APPROVE_TRANSFORMED_GOODS_PAGE
    ),
    # Retail Goods URLs
    path(
        f'{PAGES.DASHBOARD}/Retail-Goods/',
        wa_views.RetailGoodsPage,
        name=PAGES.RETAIL_GOODS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Convert-To-Retail/',
        wa_views.ConvertToRetailPage,
        name=PAGES.CONVERT_TO_RETAIL_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Add-Retail-Goods/',
        wa_views.AddRetailGoodsPage,
        name=PAGES.ADD_RETAIL_GOODS_PAGE
    ),
    # Accounting manager
    path(
        f'{PAGES.DASHBOARD}/',
        am_views.Dashboard,
        name=PAGES.ACCOUNTING_MANAGER_DASHBOARD
    ),
    path(
        f'{PAGES.DASHBOARD}/Sales/',
        am_views.SalesPage,
        name=PAGES.SALES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Add-Sales/',
        am_views.AddSalesPage,
        name=PAGES.ADD_SALES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Pricing/',
        am_views.PricingPage,
        name=PAGES.PRICING_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Expenses/',
        am_views.ExpensesPage,
        name=PAGES.EXPENSES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Add-Expenses/',
        am_views.AddExpensesPage,
        name=PAGES.ADD_EXPENSES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Update-Expense/<str:pk>/',
        am_views.UpdateExpensePage,
        name=PAGES.UPDATE_EXPENSES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Delete-Expense/<str:pk>/',
        am_views.DeleteExpensePage,
        name=PAGES.DELETE_EXPENSES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Approve-Payments/',
        am_views.ApprovePaymentsPage,
        name=PAGES.APPROVE_PAYMENTS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Approve-Payment/<str:pk>/',
        am_views.ApprovePayment,
        name=PAGES.APPROVE_PAYMENT_PAGE
    ),
]
