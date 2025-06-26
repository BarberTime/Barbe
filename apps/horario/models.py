from django.db import models
from apps.negocio.models import Negocio 
import uuid

class Horario(models.Model):
    id_horario = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE)
    dia = models.CharField(max_length=10)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    class Meta:
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        db_table = 'horario'
        ordering = ['dia', 'hora_inicio']
    
    def __str__(self):
        return f"{self.dia} - {self.hora_inicio} a {self.hora_fin}"
    
    def get_dia_display_custom(self):
        dias = {
            'lunes': 'Lunes',
            'martes': 'Martes',
            'miercoles': 'Miércoles',
            'jueves': 'Jueves',
            'viernes': 'Viernes',
            'sabado': 'Sábado',
            'domingo': 'Domingo',
        }
        return dias.get(self.dia, self.dia.capitalize())
