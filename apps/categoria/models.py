from django.db import models
import uuid
from apps.negocio.models import Negocio

class Categoria(models.Model):
    id_categoria = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        db_table = 'categoria'
    
    def __str__(self):
        return self.nombre
