from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'rol'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('editar/<uuid:id_rol>/', views.editar, name='editar'),
    path('eliminar/<uuid:id_rol>/', views.eliminar, name='eliminar'),
]
