from django.urls import path
from .views import index, crearUsuario, listaUsuarios, actualizarUsuario, eliminarUsuario, iniciarSesion, cerrarSesion

app_name = 'usuario'

urlpatterns = [
    path('', index, name="index-usuario"),
    path('crear/', crearUsuario, name='crear-usuario'),
    path('lista/', listaUsuarios, name='lista-usuarios'),
    path('actualizar/<uuid:id_usuario>/', actualizarUsuario, name='actualizar-usuario'),
    path('eliminar/<uuid:id_usuario>/', eliminarUsuario, name='eliminar-usuario'),
    path('iniciar-sesion/', iniciarSesion, name='iniciar-sesion'),
    path('cerrar-sesion/', cerrarSesion, name='cerrar-sesion'),

]