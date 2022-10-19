from django.urls import path
from . import views
from .constant import PAGES


urlpatterns = [
    path('', views.index, name=PAGES.INDEX),
    path('Error', views.unauthorized, name=PAGES.UNAUTHORIZED_PAGE),
    path('Dashboard', views.dashboard, name=PAGES.DASHBOARD),
    path('about', views.about, name=PAGES.ABOUT_PAGE),
    path('logout', views.logoutUser, name=PAGES.LOGOUT),
    path('Create-User', views.createUserPage,
         name=PAGES.CREATE_USER_PAGE),
    path('Tasks', views.tasks, name=PAGES.TASKS_PAGE),
]
