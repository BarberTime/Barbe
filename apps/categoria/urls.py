from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'categoria'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('editar/<uuid:id_categoria>/', views.editar, name='editar'),
    path('eliminar/<uuid:id_categoria>/', views.eliminar, name='eliminar'),
    path('lista-empleado/', views.lista_empleado, name='lista_empleado'),
]
