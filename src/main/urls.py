from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='Index'),
    path('Error', views.unauthorized, name='Unauthorized'),
    path('Dashboard', views.dashboard, name='Dashboard'),
    path('about', views.about, name='About'),
    path('logout', views.logoutUser, name='Logout'),
    path('Create-User', views.createUserPage, name='CreateUserPage'),
    path('Tasks', views.tasks, name='Tasks'),
]
