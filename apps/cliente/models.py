from django.db import models
from apps.usuario.models import Usuario
from apps.rol.models import Rol
from uuid import uuid4
# Create your models here.
class Cliente(models.Model):    
    id_cliente = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100,null=True,blank=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        db_table = 'cliente'
    
    def __str__(self):
        return self.nombre