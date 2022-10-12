from django.urls import URLPattern, path
from . import views

urlpatterns = [

    # ----------------------------Dashboard URLs------------------------------
    path('Dashboard', views.warehouseAdminDashboard, name='WarehouseAdminDashboard'),

    # --------------------------Main Storage URLs-----------------------------
    path('Main-Storage', views.MainStorageGoodsPage, name='MainStorageGoodsPage'),
    path('Main-Storage/<str:type>', views.DetailItemCardsPage, name='DetailItemCardsPage'),
    path('Add-Goods', views.AddGoodsPage, name='AddGoodsPage'),
    
    # -------------------------RegisteredItems URLs---------------------------
    path('Registered-Items', views.RegisteredItemsPage, name='RegisteredItemsPage'),
    path('Register-Item', views.RegisterItemPage, name='RegisterItemPage'),

    # -----------------------------Batches URLs-------------------------------
    path('Batches', views.BatchesPage, name='BatchesPage'),
    path('Add-Batch', views.AddBatchPage, name='AddBatchPage'),
    
    # ------------------------Distributed Goods URLs--------------------------
    path('Distributed-Goods', views.DistributedGoodsPage, name='DistributedGoodsPage'),
    path('Distributor-Stock/<str:pk>', views.DistributorStockPage, name="DistributorStockPage"),
    path('Send-Goods/<str:pk>', views.SendGoodsPage, name='SendGoodsPage'),

    # -------------------------Goods Movement URLs----------------------------
    path('Goods-Movement', views.GoodsMovementPage, name='GoodsMovementPage'),

    # --------------------------Damaged Goods URLs----------------------------
    path('Damaged-Goods', views.DamagedGoodsPage, name='DamagedGoodsPage'),
    path('Add-Damaged-Goods', views.AddDamagedGoodsPage, name='AddDamagedGoodsPage'),

    # -------------------------Transformed Goods URLs--------------------------
    path('Transformed-Goods', views.TransformedGoodsPage, name='TransformedGoodsPage'),
    path('Approve-Transformed/<str:pk>', views.ApproveTransformedGoods, name='ApproveTransformedGoods'),

    # ---------------------------Retail Goods URLs----------------------------
    path('Retail-Goods', views.RetailGoodsPage, name='RetailGoodsPage'),
    path('Convert-To-Retail', views.ConvertToRetailPage, name='ConvertToRetailPage'),
    path('Add-Retail-Goods', views.AddRetailGoodsPage, name='AddRetailGoodsPage'),
]
