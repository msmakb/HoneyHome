from django.urls import path
from main.constants import PAGES
from . import views as ceo_views
from human_resources import views as hr_views

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
        name=PAGES.EMPLOYEES_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Employee/Add-Employee/',
        hr_views.addEmployeePage,
        name=PAGES.ADD_EMPLOYEE_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Employee/<str:pk>/',
        hr_views.employeePage,
        name=PAGES.EMPLOYEE_RECORD_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Employee/Update/<str:pk>/',
        hr_views.updateEmployeePage,
        name=PAGES.UPDATE_EMPLOYEE_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Employee/Delete/<str:pk>/',
        hr_views.deleteEmployeePage,
        name=PAGES.DELETE_EMPLOYEE_PAGE_CEO
    ),
    # Distributors URLs
    path(
        f'{PAGES.DASHBOARD}/Distributors/',
        hr_views.distributorsPage,
        name=PAGES.DISTRIBUTORS_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor/Add-Distributor/',
        hr_views.addDistributorPage,
        name=PAGES.ADD_DISTRIBUTOR_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor/<str:pk>/',
        hr_views.distributorPage,
        name=PAGES.DISTRIBUTOR_RECORD_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor/Update/<str:pk>/',
        hr_views.updateDistributorPage,
        name=PAGES.UPDATE_DISTRIBUTOR_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor/Delete/<str:pk>/',
        hr_views.deleteDistributorPage,
        name=PAGES.DELETE_DISTRIBUTOR_PAGE_CEO
    ),
    # Tasks URLs
    path(
        f'{PAGES.DASHBOARD}/Tasks/',
        hr_views.employeeTasksPage,
        name=PAGES.EMPLOYEES_TASKS_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Task/Add-Task/',
        hr_views.addTaskPage,
        name=PAGES.ADD_TASK_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Task/<str:pk>/',
        hr_views.taskPage,
        name=PAGES.DETAILED_TASK_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Task/Update/<str:pk>/',
        hr_views.updateTaskPage,
        name=PAGES.UPDATE_TASK_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Task/Delete/<str:pk>/',
        hr_views.deleteTaskPage,
        name=PAGES.DELETE_TASK_PAGE_CEO
    ),
    # Evaluation URLs
    path(
        f'{PAGES.DASHBOARD}/Evaluation/',
        hr_views.evaluationPage,
        name=PAGES.EVALUATION_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Weekly-Evaluation/',
        hr_views.weeklyEvaluationPage,
        name=PAGES.WEEKLY_EVALUATION_PAGE_CEO
    ),
    path(
        f'{PAGES.DASHBOARD}/Task-Evaluation/',
        hr_views.taskEvaluationPage,
        name=PAGES.TASK_EVALUATION_PAGE_CEO
    ),
]
