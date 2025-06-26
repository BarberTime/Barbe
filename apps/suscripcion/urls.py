from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'suscripcion'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('editar/<uuid:id_suscripcion>/', views.editar, name='editar'),
    path('eliminar/<uuid:id_suscripcion>/', views.eliminar, name='eliminar'),
    path('renovar/<uuid:id_suscripcion>/', views.renovar, name='renovar'),
    
    # Planes
    path('planes/', views.planes_index, name='planes_index'),
    path('planes/crear/', views.plan_crear, name='plan_crear'),
]
