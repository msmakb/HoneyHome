from django.urls import path

from main.constants import PAGES

from . import views


app_name = 'distributor'
urlpatterns = [
    path(
        f'{PAGES.DASHBOARD}/',
        views.Dashboard,
        name=PAGES.DISTRIBUTOR_DASHBOARD
    ),
    path(
        f'{PAGES.DASHBOARD}/Goods',
        views.GoodsPage,
        name=PAGES.GOODS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Send-Payment',
        views.SendPaymentPage,
        name=PAGES.SEND_PAYMENT_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Freeze-Item',
        views.FreezeItemPage,
        name=PAGES.FREEZE_ITEMS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Return-Item',
        views.ReturnItemPage,
        name=PAGES.RETURN_ITEMS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/History',
        views.HistoryPage,
        name=PAGES.HISTORY_PAGE
    ),
]
