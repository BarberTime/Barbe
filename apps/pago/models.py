from django.db import models
from apps.reserva.models import Reserva 
import uuid   

class Pago(models.Model):
    id_pago = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=10)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        db_table = 'pago'
    
    def __str__(self):
        return self.id_pago