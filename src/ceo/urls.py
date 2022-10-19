from django.urls import path
from main.constant import PAGES
from human_resources import views as hr_views
from . import views

urlpatterns = [
    path('Dashboard', views.Dashboard, name=PAGES.CEO_DASHBOARD),

    # ----------------------------Employees URLs------------------------------ #
    path('Employees/', hr_views.EmployeesPage, name=PAGES.EMPLOYEES_PAGE_CEO),
    path('Employee/Add-Employee', hr_views.AddEmployeePage,
         name=PAGES.ADD_EMPLOYEE_PAGE_CEO),
    path('Employee/<str:pk>', hr_views.EmployeePage,
         name=PAGES.EMPLOYEE_RECORD_PAGE_CEO),
    path('Employee/Update/<str:pk>', hr_views.UpdateEmployeePage,
         name=PAGES.UPDATE_EMPLOYEE_PAGE_CEO),
    path('Employee/Delete/<str:pk>', hr_views.DeleteEmployeePage,
         name=PAGES.DELETE_EMPLOYEE_PAGE_CEO),

    # ----------------------------Distributors URLs--------------------------- #
    path('Distributors/', hr_views.DistributorsPage,
         name=PAGES.DISTRIBUTORS_PAGE_CEO),
    path('Distributor/Add-Distributor', hr_views.AddDistributorPage,
         name=PAGES.ADD_DISTRIBUTOR_PAGE_CEO),
    path('Distributor/<str:pk>', hr_views.DistributorPage,
         name=PAGES.DISTRIBUTOR_RECORD_PAGE_CEO),
    path('Distributor/Update/<str:pk>', hr_views.UpdateDistributorPage,
         name=PAGES.UPDATE_DISTRIBUTOR_PAGE_CEO),
    path('Distributor/Delete/<str:pk>', hr_views.DeleteDistributorPage,
         name=PAGES.DELETE_DISTRIBUTOR_PAGE_CEO),

    # ----------------------------Tasks URLs---------------------------------- #
    path('Tasks', hr_views.TasksPage.as_view(),
         name=PAGES.EMPLOYEES_TASKS_PAGE_CEO),
    path('Task/Add-Task', hr_views.AddTaskPage, name=PAGES.ADD_TASK_PAGE_CEO),
    path('Task/<str:pk>', hr_views.TaskPage, name="TaskPage-CEO"),
    path('Task/Update/<str:pk>', hr_views.UpdateTaskPage,
         name=PAGES.UPDATE_TASK_PAGE_CEO),
    path('Task/Delete/<str:pk>', hr_views.DeleteTaskPage,
         name=PAGES.DELETE_TASK_PAGE_CEO),

    # ------------------------------Evaluation URLs--------------------------- #
    path('Evaluation', hr_views.EvaluationPage, name=PAGES.EVALUATION_PAGE_CEO),
    path('Weekly-Evaluation', hr_views.WeeklyEvaluationPage,
         name=PAGES.WEEKLY_EVALUATION_PAGE_CEO),
    path('Task-Evaluation', hr_views.TaskEvaluationPage,
         name=PAGES.TASK_EVALUATION_PAGE_CEO),
]
