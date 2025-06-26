from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'cliente'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('editar/<uuid:id_cliente>/', views.editar, name='editar'),
    path('eliminar/<uuid:id_cliente>/', views.eliminar, name='eliminar'),
    path('detalle/<uuid:id_cliente>/', views.detalle, name='detalle'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
