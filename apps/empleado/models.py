# apps/empleado/models.py
from django.db import models
from apps.usuario.models import Usuario
from apps.negocio.models import Negocio
from apps.rol.models import Rol
import uuid


class Empleado(models.Model):
    id_empleado = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, default=None)
    especialidad = models.CharField(max_length=100)
    experiencia_anios = models.IntegerField()
    foto_perfil = models.ImageField(upload_to='empleados/fotos/', null=True, blank=True)
    fecha_contratacion = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        db_table = 'empleados'

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.especialidad}"

        