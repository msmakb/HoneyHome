from django.urls import path
from main.constant import PAGES
from . import views

urlpatterns = [

    # ----------------------------Dashboard URLs------------------------------
    path('Dashboard', views.warehouseAdminDashboard,
         name=PAGES.WAREHOUSE_ADMIN_DASHBOARD),

    # --------------------------Main Storage URLs-----------------------------
    path('Main-Storage', views.MainStorageGoodsPage,
         name=PAGES.MAIN_STORAGE_GOODS_PAGE),
    path('Main-Storage/<str:type>', views.DetailItemCardsPage,
         name=PAGES.DETAIL_ITEM_CARDS_PAGE),
    path('Add-Goods', views.AddGoodsPage, name=PAGES.ADD_GOODS_PAGE),

    # -------------------------RegisteredItems URLs---------------------------
    path('Registered-Items', views.RegisteredItemsPage,
         name=PAGES.REGISTERED_ITEMS_PAGE),
    path('Register-Item', views.RegisterItemPage,
         name=PAGES.REGISTER_NEW_ITEM_PAGE),

    # -----------------------------Batches URLs-------------------------------
    path('Batches', views.BatchesPage, name=PAGES.BATCHES_PAGE),
    path('Add-Batch', views.AddBatchPage, name=PAGES.ADD_BATCH_PAGE),

    # ------------------------Distributed Goods URLs--------------------------
    path('Distributed-Goods', views.DistributedGoodsPage,
         name=PAGES.DISTRIBUTED_GOODS_PAGE),
    path('Distributor-Stock/<str:pk>',
         views.DistributorStockPage, name=PAGES.DISTRIBUTOR_STOCK_PAGE),
    path('Send-Goods/<str:pk>', views.SendGoodsPage, name=PAGES.SEND_GOODS_PAGE),

    # -------------------------Goods Movement URLs----------------------------
    path('Goods-Movement', views.GoodsMovementPage,
         name=PAGES.GOODS_MOVEMENT_PAGE),

    # --------------------------Damaged Goods URLs----------------------------
    path('Damaged-Goods', views.DamagedGoodsPage, name=PAGES.DAMAGED_GOODS_PAGE),
    path('Add-Damaged-Goods', views.AddDamagedGoodsPage,
         name=PAGES.ADD_DAMAGED_GOODS_PAGE),

    # -------------------------Transformed Goods URLs--------------------------
    path('Transformed-Goods', views.TransformedGoodsPage,
         name=PAGES.TRANSFORMED_GOODS_PAGE),
    path('Approve-Transformed/<str:pk>', views.ApproveTransformedGoods,
         name=PAGES.APPROVE_TRANSFORMED_GOODS_PAGE),

    # ---------------------------Retail Goods URLs----------------------------
    path('Retail-Goods', views.RetailGoodsPage, name=PAGES.RETAIL_GOODS_PAGE),
    path('Convert-To-Retail', views.ConvertToRetailPage,
         name=PAGES.CONVERT_TO_RETAIL_PAGE),
    path('Add-Retail-Goods', views.AddRetailGoodsPage,
         name=PAGES.ADD_RETAIL_GOODS_PAGE),
]
