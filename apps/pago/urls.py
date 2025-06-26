from django.urls import path
from . import views

app_name = 'pago'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('editar/<uuid:id_pago>/', views.editar, name='editar'),
    path('eliminar/<uuid:id_pago>/', views.eliminar, name='eliminar'),
    path('detalle/<uuid:id_pago>/', views.detalle, name='detalle'),
]
