from django.contrib import admin
from django.urls import path, include
from . import views
from apps.reserva import views as reserva_views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'web'
urlpatterns = [
    path('', views.index, name='index'),
    path('detalle-negocio/<uuid:negocio_id>/', views.detalle_negocio, name='detalle_negocio'),
    
    # Autenticación de clientes
    path('iniciar-sesion-cliente/', views.iniciar_sesion_cliente, name='iniciar_sesion_cliente'),
    path('registrar-cliente/', views.registrar_cliente, name='registrar_cliente'),
    path('cerrar-sesion-cliente/', views.cerrar_sesion_cliente, name='cerrar_sesion_cliente'),
    
    # Registro de negocios
    path('registrar-negocio/', views.registrar_negocio, name='registrar_negocio'),
    
    # Reservas
    path('crear-reserva/', views.crear_reserva, name='crear_reserva'),
    path('cancelar-reserva/', views.cancelar_reserva, name='cancelar_reserva'),
    
    # Autenticación de administradores
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/superadmin/', views.dashboard_superadmin, name='dashboard_superadmin'),
    path('dashboard/barbero/', views.dashboard_barbero, name='dashboard_barbero'),
    path('dashboard/empleado/', views.dashboard_empleado, name='dashboard_empleado'),
    
    # Superadmin views
    path('superadmin-negocio/', views.superadmin_negocio, name='superadmin_negocio'),
    path('superadmin-usuario/', views.superadmin_usuario, name='superadmin_usuario'),
    path('superadmin-usuario/crear/', views.superadmin_usuario_crear, name='superadmin_usuario_crear'),
    path('superadmin-usuario/crear-empleado/', views.crear_empleado, name='superadmin_usuario_crear_empleado'),
    path('superadmin-usuario/editar/<uuid:id_usuario>/', views.superadmin_usuario_editar, name='superadmin_usuario_editar'),
    path('superadmin-usuario/eliminar/<uuid:id_usuario>/', views.superadmin_usuario_eliminar, name='superadmin_usuario_eliminar'),
    path('superadmin-suscripcion/', views.superadmin_suscripcion, name='superadmin_suscripcion'),
    path('superadmin-reserva/', views.superadmin_reserva, name='superadmin_reserva'),
    
    # CRUD suscripciones
    path('superadmin-suscripcion/editar/<int:id_suscripcion>/', views.superadmin_suscripcion_editar, name='superadmin_suscripcion_editar'),
    path('superadmin-suscripcion/eliminar/<int:id_suscripcion>/', views.superadmin_suscripcion_eliminar, name='superadmin_suscripcion_eliminar'),
    
    # Perfil
    path('perfil/', views.perfil, name='perfil'),
    path('check-employee-availability/', views.check_employee_availability, name='check_employee_availability'),
]


