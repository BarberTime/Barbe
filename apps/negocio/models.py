from django.db import models
from apps.usuario.models import Usuario
import uuid


class Negocio(models.Model):
    choices_departamentos = (
        ('La Paz', 'La Paz'),
        ('Cochabamba', 'Cochabamba'),
        ('Santa Cruz', 'Santa Cruz'),
        ('Oruro', 'Oruro'),
        ('Potosí', 'Potosí'),
        ('Tarija', 'Tarija'),
        ('Beni', 'Beni'),
        ('Pando', 'Pando'),
        ('Chuquisaca', 'Chuquisaca'),
    )
    id_negocio = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    descripcion = models.TextField(max_length=500)
    departamento = models.CharField(max_length=100, choices=choices_departamentos, null=True, blank=True, default='La Paz')
    direccion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=10)
    longitud = models.DecimalField(max_digits=30, decimal_places=25)
    latitud = models.DecimalField(max_digits=30, decimal_places=25)
    logo = models.ImageField(upload_to='negocios/logos/', null=True, blank=True)
    foto = models.ImageField(upload_to='negocios/fotos/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Negocio'
        verbose_name_plural = 'Negocios'
        db_table = 'negocio'
    
    def __str__(self):
        return self.nombre
    
