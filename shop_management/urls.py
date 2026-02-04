from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='sales/pos/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('tenants/', include('tenants.urls')),
    path('api/', include('api.urls')),
    path('inventory/', include('inventory.urls')),
    path('customers/', include('customers.urls')),
    path('sales/', include('sales.urls')),
    path('reports/', include('reports.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

