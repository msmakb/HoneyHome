from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from main.constants import ADMIN_SITE


urlpatterns = [

    # Admin URLs
    path('admin/', admin.site.urls),

    # Main app URLs
    path('', include('main.urls')),

    # System apps URLs
    # Note: the url must be the same as the role.
    # check 'AllowedUserMiddleware'
    path('HumanResources/', include('human_resources.urls', namespace='HumanResources')),
    path('WarehouseAdmin/', include('warehouse_admin.urls', namespace='WarehouseAdmin')),
    path('SocialMediaManager/', include('social_media_manager.urls',
         namespace='SocialMediaManager')),
    path('AccountingManager/', include('accounting_manager.urls',
         namespace='AccountingManager')),
    path('Distributor/', include('distributor.urls', namespace='Distributor')),
    path('CEO/', include('ceo.urls', namespace='CEO')),
]

# Static and Media URL Patterns
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site settings
admin.site.site_header = ADMIN_SITE.SITE_HEADER
admin.site.site_title = ADMIN_SITE.SITE_TITLE
admin.site.index_title = ADMIN_SITE.INDEX_TITLE
