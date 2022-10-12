from django.urls import path
from . import views


urlpatterns = [

    # ----------------------------Dashboard URLs------------------------------ #
    path('Dashboard/', views.humanResourcesDashboard, name='HumanResourcesDashboard'),

    # ----------------------------Employees URLs------------------------------ #
    path('Employees/', views.EmployeesPage, name="EmployeesPage"),
    path('Employee/Add-Employee', views.AddEmployeePage, name="AddEmployeePage"),
    path('Employee/<str:pk>', views.EmployeePage, name="EmployeePage"),
    path('Employee/Update/<str:pk>', views.UpdateEmployeePage, name="UpdateEmployeePage"),
    path('Employee/Delete/<str:pk>', views.DeleteEmployeePage, name="DeleteEmployeePage"),

    # ----------------------------Distributors URLs--------------------------- #
    path('Distributors/', views.DistributorsPage, name="DistributorsPage"),
    path('Distributor/Add-Distributor', views.AddDistributorPage, name="AddDistributorPage"),
    path('Distributor/<str:pk>', views.DistributorPage, name="DistributorPage"),
    path('Distributor/Update/<str:pk>', views.UpdateDistributorPage, name="UpdateDistributorPage"),
    path('Distributor/Delete/<str:pk>', views.DeleteDistributorPage, name="DeleteDistributorPage"),

    # ----------------------------Tasks URLs---------------------------------- #
    path('Tasks', views.TasksPage.as_view(), name="TasksPage"),
    path('Task/Add-Task', views.AddTaskPage, name="AddTaskPage"),
    path('Task/<str:pk>', views.TaskPage, name="TaskPage"),
    path('Task/Update/<str:pk>', views.UpdateTaskPage, name="UpdateTaskPage"),
    path('Task/Delete/<str:pk>', views.DeleteTaskPage, name="DeleteTaskPage"),

    # ------------------------------Evaluation URLs--------------------------- #
    path('Evaluation', views.EvaluationPage, name="EvaluationPage"),
    path('Weekly-Evaluation', views.WeeklyEvaluationPage, name='WeeklyEvaluationPage'),
    path('Task-Evaluation', views.TaskEvaluationPage, name='TaskEvaluationPage'),
]
