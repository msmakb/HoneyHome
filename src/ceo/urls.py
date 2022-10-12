from django.urls import path
from human_resources import views as hr_views
from . import views

urlpatterns = [
    path('Dashboard', views.Dashboard, name='CEODashboard'),

     # ----------------------------Employees URLs------------------------------ #
    path('Employees/', hr_views.EmployeesPage, name="EmployeesPage-CEO"),
    path('Employee/Add-Employee', hr_views.AddEmployeePage, name="AddEmployeePage-CEO"),
    path('Employee/<str:pk>', hr_views.EmployeePage, name="EmployeePage-CEO"),
    path('Employee/Update/<str:pk>', hr_views.UpdateEmployeePage, name="UpdateEmployeePage-CEO"),
    path('Employee/Delete/<str:pk>', hr_views.DeleteEmployeePage, name="DeleteEmployeePage-CEO"),

    # ----------------------------Distributors URLs--------------------------- #
    path('Distributors/', hr_views.DistributorsPage, name="DistributorsPage-CEO"),
    path('Distributor/Add-Distributor', hr_views.AddDistributorPage, name="AddDistributorPage-CEO"),
    path('Distributor/<str:pk>', hr_views.DistributorPage, name="DistributorPage-CEO"),
    path('Distributor/Update/<str:pk>', hr_views.UpdateDistributorPage, name="UpdateDistributorPage-CEO"),
    path('Distributor/Delete/<str:pk>', hr_views.DeleteDistributorPage, name="DeleteDistributorPage-CEO"),

    # ----------------------------Tasks URLs---------------------------------- #
    path('Tasks', hr_views.TasksPage.as_view(), name="TasksPage-CEO"),
    path('Task/Add-Task', hr_views.AddTaskPage, name="AddTaskPage-CEO"),
    path('Task/<str:pk>', hr_views.TaskPage, name="TaskPage-CEO"),
    path('Task/Update/<str:pk>', hr_views.UpdateTaskPage, name="UpdateTaskPage-CEO"),
    path('Task/Delete/<str:pk>', hr_views.DeleteTaskPage, name="DeleteTaskPage-CEO"),

    # ------------------------------Evaluation URLs--------------------------- #
    path('Evaluation', hr_views.EvaluationPage, name="EvaluationPage-CEO"),
    path('Weekly-Evaluation', hr_views.WeeklyEvaluationPage, name='WeeklyEvaluationPage-CEO'),
    path('Task-Evaluation', hr_views.TaskEvaluationPage, name='TaskEvaluationPage-CEO'),
]