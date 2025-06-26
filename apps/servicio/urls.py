from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'servicio'

urlpatterns = [
    # URLs para servicios
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('editar/<uuid:id_servicio>/', views.editar, name='editar'),
    path('eliminar/<uuid:id_servicio>/', views.eliminar, name='eliminar'),
    path('lista-empleado/', views.lista_empleado, name='lista_empleado'),
    
    # URLs para categorías de servicio
    path('categoria/', views.categoria_index, name='categoria_index'),
    path('categoria/crear/', views.categoria_crear, name='categoria_crear'),
    path('categoria/editar/<uuid:id_categoria>/', views.categoria_editar, name='categoria_editar'),
    path('categoria/eliminar/<uuid:id_categoria>/', views.categoria_eliminar, name='categoria_eliminar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
