from django.urls import path
from .views import index, crearImagenesNegocio, listaImagenesNegocio, actualizarImagenesNegocio, eliminarImagenesNegocio
from django.conf import settings
from django.conf.urls.static import static
app_name = 'imagenes_negocio'
urlpatterns = [
    path('', index, name="index-imagenes_negocio"),
    path('crear/', crearImagenesNegocio, name='crear-imagenes_negocio'),
    path('lista/', listaImagenesNegocio, name='lista-imagenes_negocio'),
    path('actualizar/<int:id_imagen>/', actualizarImagenesNegocio, name='actualizar-imagenes_negocio'),
    path('eliminar/<int:id_imagen>/', eliminarImagenesNegocio, name='eliminar-imagenes_negocio'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)