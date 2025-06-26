from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'usuario_rol'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('editar/<uuid:id_usuario_rol>/', views.editar, name='editar'),
    path('eliminar/<uuid:id_usuario_rol>/', views.eliminar, name='eliminar'),
]
