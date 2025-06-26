from django.db import models
from apps.usuario.models import Usuario
from apps.rol.models import Rol
import uuid

class UsuarioRol(models.Model):
    id_usuario_rol = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Usuario Rol'
        verbose_name_plural = 'Usuarios Roles'
        db_table = 'usuario_rol'
    
    def __str__(self):
        return f"{self.usuario.usuario} - {self.rol.nombre}"
