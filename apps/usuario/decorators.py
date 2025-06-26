from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from apps.usuario_rol.models import UsuarioRol
from apps.usuario.models import Usuario

def rol_requerido(roles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                # Get user from session
                usuario_id = request.session.get('usuario_id')
                if not usuario_id:
                    return redirect('web:login')
                
                # Get user and their roles
                usuario = Usuario.objects.get(id_usuario=usuario_id)
                usuario_rol = UsuarioRol.objects.get(usuario=usuario)
                rol_actual = usuario_rol.rol.nombre.lower()
                
                # Check if role is allowed
                if rol_actual in roles_permitidos:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, 'No tienes permisos para acceder a esta página')
                    return redirect('web:dashboard')
            except UsuarioRol.DoesNotExist:
                messages.error(request, 'No tienes un rol asignado')
                return redirect('web:dashboard')
            except Usuario.DoesNotExist:
                return redirect('web:login')
        return _wrapped_view
    return decorator

# Specific decorators
def es_barbero(view_func):
    return rol_requerido(['barbero'])(view_func)

def es_superadmin(view_func):
    return rol_requerido(['superadmin'])(view_func)

def es_empleado(view_func):
    return rol_requerido(['empleado'])(view_func)

def es_barbero_o_superadmin(view_func):
    return rol_requerido(['barbero', 'superadmin'])(view_func)

def cualquier_rol_admin(view_func):
    return rol_requerido(['barbero', 'superadmin', 'empleado'])(view_func)
