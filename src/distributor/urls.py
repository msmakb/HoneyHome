from django.urls import path
from . import views


urlpatterns = [
    path('Dashboard', views.Dashboard, name='DistributorDashboard'),
    path('Goods', views.GoodsPage, name='GoodsPage'),
    path('Send-Payment', views.SendPaymentPage, name='SendPaymentPage'),
    path('Freeze-Item', views.FreezeItemPage, name='FreezeItemPage'),
    path('Return-Item', views.ReturnItemPage, name='ReturnItemPage'),
    path('History', views.HistoryPage, name='HistoryPage'),
]