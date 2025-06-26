from django.contrib.auth.decorators import login_required
from apps.usuario.models import Usuario
from apps.usuario_rol.models import UsuarioRol
from apps.negocio.models import Negocio
from django.conf import settings

def usuario_rol(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)
            usuario_rol = UsuarioRol.objects.filter(usuario=usuario).first()
            return {'usuario_rol': usuario_rol}
        except Usuario.DoesNotExist:
            return {'usuario_rol': None}
    return {'usuario_rol': None}

def negocio_context(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)
            try:
                negocio = Negocio.objects.get(usuario=usuario)
                return {'negocio': negocio}
            except Negocio.DoesNotExist:
                return {'negocio': None}
        except Usuario.DoesNotExist:
            return {'negocio': None}
    return {'negocio': None}
