from django.db import models
import uuid
from apps.negocio.models import Negocio
from apps.categoria.models import Categoria


class Servicio(models.Model):
    id_servicio = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2) 
    descripcion = models.TextField()
    duracion = models.IntegerField()
    imagen = models.ImageField(upload_to='servicios/imagenes/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='activo')
    
    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        db_table = 'servicio'
    
    def __str__(self):
        return self.nombre
