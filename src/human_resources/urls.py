from django.urls import path
from main.constant import PAGES
from . import views


urlpatterns = [

    # ----------------------------Dashboard URLs------------------------------ #
    path('Dashboard/', views.humanResourcesDashboard,
         name=PAGES.HUMAN_RESOURCES_DASHBOARD),

    # ----------------------------Employees URLs------------------------------ #
    path('Employees/', views.EmployeesPage, name=PAGES.EMPLOYEES_PAGE),
    path('Employee/Add-Employee', views.AddEmployeePage,
         name=PAGES.ADD_EMPLOYEE_PAGE),
    path('Employee/<str:pk>', views.EmployeePage,
         name=PAGES.EMPLOYEE_RECORD_PAGE),
    path('Employee/Update/<str:pk>', views.UpdateEmployeePage,
         name=PAGES.UPDATE_EMPLOYEE_PAGE),
    path('Employee/Delete/<str:pk>', views.DeleteEmployeePage,
         name=PAGES.DELETE_EMPLOYEE_PAGE),

    # ----------------------------Distributors URLs--------------------------- #
    path('Distributors/', views.DistributorsPage, name=PAGES.DISTRIBUTORS_PAGE),
    path('Distributor/Add-Distributor', views.AddDistributorPage,
         name=PAGES.ADD_DISTRIBUTOR_PAGE),
    path('Distributor/<str:pk>', views.DistributorPage,
         name=PAGES.DISTRIBUTOR_RECORD_PAGE),
    path('Distributor/Update/<str:pk>', views.UpdateDistributorPage,
         name=PAGES.UPDATE_DISTRIBUTOR_PAGE),
    path('Distributor/Delete/<str:pk>', views.DeleteDistributorPage,
         name=PAGES.UPDATE_DISTRIBUTOR_PAGE),

    # ----------------------------Tasks URLs---------------------------------- #
    path('Tasks', views.TasksPage.as_view(), name=PAGES.EMPLOYEES_TASKS_PAGE),
    path('Task/Add-Task', views.AddTaskPage, name=PAGES.ADD_TASK_PAGE),
    path('Task/<str:pk>', views.TaskPage, name=PAGES.DETAILED_TASK_PAGE),
    path('Task/Update/<str:pk>', views.UpdateTaskPage,
         name=PAGES.UPDATE_TASK_PAGE),
    path('Task/Delete/<str:pk>', views.DeleteTaskPage,
         name=PAGES.DELETE_TASK_PAGE),

    # ------------------------------Evaluation URLs--------------------------- #
    path('Evaluation', views.EvaluationPage, name=PAGES.EVALUATION_PAGE),
    path('Weekly-Evaluation', views.WeeklyEvaluationPage,
         name=PAGES.WEEKLY_EVALUATION_PAGE),
    path('Task-Evaluation', views.TaskEvaluationPage,
         name=PAGES.TASK_EVALUATION_PAGE),
]
