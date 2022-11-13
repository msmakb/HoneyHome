from django.urls import path
from main.constants import PAGES
from main.views import tasks
from . import views

app_name = 'warehouse_admin'
urlpatterns = [

    # ----------------------------Dashboard URLs------------------------------
    path(
        f'{PAGES.DASHBOARD}/',
        views.warehouseAdminDashboard,
        name=PAGES.WAREHOUSE_ADMIN_DASHBOARD
    ),
    # --------------------------Main Storage URLs-----------------------------
    path(
        f'{PAGES.DASHBOARD}/Main-Storage/',
        views.MainStorageGoodsPage,
        name=PAGES.MAIN_STORAGE_GOODS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Main-Storage/<str:type>/',
        views.DetailItemCardsPage,
        name=PAGES.DETAIL_ITEM_CARDS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Add-Goods/',
        views.AddGoodsPage,
        name=PAGES.ADD_GOODS_PAGE
    ),

    # -------------------------RegisteredItems URLs---------------------------
    path(
        f'{PAGES.DASHBOARD}/Registered-Items/',
        views.RegisteredItemsPage,
        name=PAGES.REGISTERED_ITEMS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Register-Item/',
        views.RegisterItemPage,
        name=PAGES.REGISTER_NEW_ITEM_PAGE
    ),

    # Batches URLs
    path(
        f'{PAGES.DASHBOARD}/Batches/',
        views.BatchesPage,
        name=PAGES.BATCHES_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Add-Batch/',
        views.AddBatchPage,
        name=PAGES.ADD_BATCH_PAGE
    ),
    # Distributed Goods URLs
    path(
        f'{PAGES.DASHBOARD}/Distributed-Goods/',
        views.DistributedGoodsPage,
        name=PAGES.DISTRIBUTED_GOODS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Distributor-Stock/<str:pk>',
        views.DistributorStockPage,
        name=PAGES.DISTRIBUTOR_STOCK_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Send-Goods/<str:pk>/',
        views.SendGoodsPage,
        name=PAGES.SEND_GOODS_PAGE
    ),
    # Goods Movement URLs
    path(
        f'{PAGES.DASHBOARD}/Goods-Movement/',
        views.GoodsMovementPage,
        name=PAGES.GOODS_MOVEMENT_PAGE
    ),
    # Damaged Goods URLs
    path(
        f'{PAGES.DASHBOARD}/Damaged-Goods/',
        views.DamagedGoodsPage,
        name=PAGES.DAMAGED_GOODS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Add-Damaged-Goods/',
        views.AddDamagedGoodsPage,
        name=PAGES.ADD_DAMAGED_GOODS_PAGE
    ),
    # Transformed Goods URLs
    path(
        f'{PAGES.DASHBOARD}/Transformed-Goods/',
        views.TransformedGoodsPage,
        name=PAGES.TRANSFORMED_GOODS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Approve-Transformed/<str:pk>/',
        views.ApproveTransformedGoods,
        name=PAGES.APPROVE_TRANSFORMED_GOODS_PAGE
    ),
    # Retail Goods URLs
    path(
        f'{PAGES.DASHBOARD}/Retail-Goods/',
        views.RetailGoodsPage,
        name=PAGES.RETAIL_GOODS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Convert-To-Retail/',
        views.ConvertToRetailPage,
        name=PAGES.CONVERT_TO_RETAIL_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/Add-Retail-Goods/',
        views.AddRetailGoodsPage,
        name=PAGES.ADD_RETAIL_GOODS_PAGE
    ),
    path(
        f'{PAGES.DASHBOARD}/My-Tasks/',
        tasks,
        name=PAGES.TASKS_PAGE
    ),
]
