from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'reserva'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('editar/<uuid:id_reserva>/', views.editar, name='editar'),
    path('eliminar/<uuid:id_reserva>/', views.eliminar, name='eliminar'),
    path('cambiar-estado/<uuid:id_reserva>/', views.cambiar_estado, name='cambiar_estado'),
    path('calendario/', views.calendario, name='calendario'),
    path('calendario-empleado/', views.calendario_empleado, name='calendario_empleado'),
]
