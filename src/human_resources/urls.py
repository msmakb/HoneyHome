from django.urls import path
from main.constants import PAGES
from main.views import tasks
from . import views

urlpatterns = [
    # Dashboard URL
    path(
        f'{PAGES.DASHBOARD}/',
        views.humanResourcesDashboard,
        name=PAGES.HUMAN_RESOURCES_DASHBOARD
    ),
    # Employees URLs
    path(
        f'{PAGES.DASHBOARD}/Employees/',
        views.employeesPage,
        name=PAGES.EMPLOYEES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Employee/Add-Employee/',
        views.addEmployeePage,
        name=PAGES.ADD_EMPLOYEE_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Employee/<str:pk>/',
        views.employeePage,
        name=PAGES.EMPLOYEE_RECORD_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Employee/Update/<str:pk>/',
        views.updateEmployeePage,
        name=PAGES.UPDATE_EMPLOYEE_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Employee/Delete/<str:pk>/',
        views.deleteEmployeePage,
        name=PAGES.DELETE_EMPLOYEE_PAGE
    ),
    # Distributors URLs
    path(
        f'{PAGES.DASHBOARD}/Distributors/',
        views.distributorsPage,
        name=PAGES.DISTRIBUTORS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor/Add-Distributor/',
        views.addDistributorPage,
        name=PAGES.ADD_DISTRIBUTOR_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor/<str:pk>/',
        views.distributorPage,
        name=PAGES.DISTRIBUTOR_RECORD_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor/Update/<str:pk>/',
        views.updateDistributorPage,
        name=PAGES.UPDATE_DISTRIBUTOR_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor/Delete/<str:pk>/',
        views.deleteDistributorPage,
        name=PAGES.DELETE_DISTRIBUTOR_PAGE
    ),
    # Tasks URLs
    path(
        f'{PAGES.DASHBOARD}/Tasks/',
        views.employeeTasksPage,
        name=PAGES.EMPLOYEES_TASKS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Task/Add-Task/',
        views.addTaskPage,
        name=PAGES.ADD_TASK_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Task/<str:pk>/',
        views.taskPage,
        name=PAGES.DETAILED_TASK_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Task/Update/<str:pk>/',
        views.updateTaskPage,
        name=PAGES.UPDATE_TASK_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Task/Delete/<str:pk>/',
        views.deleteTaskPage,
        name=PAGES.DELETE_TASK_PAGE
    ),
    # Evaluation URLs
    path(
        f'{PAGES.DASHBOARD}/Evaluation/',
        views.evaluationPage,
        name=PAGES.EVALUATION_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Weekly-Evaluation/',
        views.weeklyEvaluationPage,
        name=PAGES.WEEKLY_EVALUATION_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Task-Evaluation/',
        views.taskEvaluationPage,
        name=PAGES.TASK_EVALUATION_PAGE
    ),
]
