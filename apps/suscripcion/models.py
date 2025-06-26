from django.db import models
import uuid
from django.utils import timezone
from apps.negocio.models import Negocio

class Plan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_dias = models.IntegerField()
    max_reservas = models.IntegerField()
    max_servicios = models.IntegerField()
    max_horarios = models.IntegerField()
    soporte_prioritario = models.BooleanField(default=False)
    estadisticas_avanzadas = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Planes'
        db_table = 'plan'
        ordering = ['precio_mensual']

    def __str__(self):
        return self.nombre

class Suscripcion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='suscripciones')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=[
        ('ACTIVA', 'Activa'),
        ('INACTIVA', 'Inactiva'),
        ('VENCIDA', 'Vencida'),
        ('CANCELADA', 'Cancelada')
    ], default='ACTIVA')
    fecha_ultimo_pago = models.DateTimeField(null=True, blank=True)
    fecha_proximo_pago = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'
        db_table = 'suscripcion'
        unique_together = ('negocio', 'plan')

    def __str__(self):
        return f"{self.negocio.nombre} - {self.plan.nombre}"

    def esta_activa(self):
        return self.estado == 'ACTIVA' and self.fecha_expiracion > timezone.now()

    def dias_restantes(self):
        if self.fecha_expiracion:
            return (self.fecha_expiracion - timezone.now()).days
        return 0

    def renovar(self):
        self.fecha_expiracion = timezone.now() + timezone.timedelta(days=self.plan.duracion_dias)
        self.estado = 'ACTIVA'
        self.fecha_ultimo_pago = timezone.now()
        self.fecha_proximo_pago = self.fecha_expiracion
        self.save()
