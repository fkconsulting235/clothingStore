from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('panel/', include('apps.dashboard.urls')),
    path('', include('apps.catalog.urls')),
    path('reservas/', include('apps.reservations.urls')),
    path('pedidos/', include('apps.orders.urls')),
]

# Sin bucket externo (S3/Supabase Storage) configurado todavía, así que Django sirve los
# archivos subidos (fotos de prendas, comprobantes) también en producción, no solo en DEBUG.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
