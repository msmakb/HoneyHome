from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # Admin URLs
    path('admin/', admin.site.urls),

    # Main app URLs
    path('', include('main.urls')),
    
    # Sytem apps URLs
    path('HumanResources/', include('human_resources.urls')),
    path('WarehouseAdmin/', include('warehouse_admin.urls')),
    path('SocialMediaManager/', include('social_media_manager.urls')),
    path('AccountingManager/', include('accounting_manager.urls')),
    path('Distributor/', include('distributor.urls')),
    path('CEO/', include('ceo.urls')),
]

# Static and Media URL Patterns
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
