from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from apps.usuario_rol.models import UsuarioRol
from apps.usuario.models import Usuario

def rol_requerido(roles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Obtener el usuario desde la sesión
            usuario_id = request.session.get('usuario_id')
            if not usuario_id:
                return redirect('web:login')
            
            try:
                # Buscar el usuario
                usuario = Usuario.objects.get(id_usuario=usuario_id)
                
                # Obtener todos los roles del usuario
                roles_usuario = UsuarioRol.objects.filter(usuario=usuario)
                
                # Verificar si alguno de los roles coincide con los permitidos
                roles_permitidos_lower = [rol.lower().strip() for rol in roles_permitidos]
                
                tiene_rol_permitido = any(
                    rol.rol.nombre.lower().strip() in roles_permitidos_lower 
                    for rol in roles_usuario
                )
                
                if tiene_rol_permitido:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden("No tienes permisos para acceder a esta página")
            except Usuario.DoesNotExist:
                return redirect('web:login')
            except UsuarioRol.DoesNotExist:
                return redirect('web:login')
        return _wrapped_view
    return decorator

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
