from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Suscripcion, Plan
from apps.negocio.models import Negocio
from apps.web.decorators import es_superadmin, es_barbero_o_superadmin
from django.utils import timezone
from datetime import timedelta

@es_superadmin
def index(request):
    suscripciones = Suscripcion.objects.all().order_by('-fecha_inicio')
    return render(request, 'modulos/suscripcion/index.html', {'suscripciones': suscripciones})

@es_superadmin
def crear(request):
    if request.method == 'POST':
        negocio_id = request.POST['negocio']
        plan_id = request.POST['plan']
        
        negocio = Negocio.objects.get(id_negocio=negocio_id)
        plan = Plan.objects.get(id=plan_id)
        
        # Calcular fecha de expiración
        fecha_expiracion = timezone.now() + timedelta(days=plan.duracion_dias)
        
        suscripcion = Suscripcion.objects.create(
            negocio=negocio,
            plan=plan,
            fecha_expiracion=fecha_expiracion,
            estado='ACTIVA',
            fecha_ultimo_pago=timezone.now(),
            fecha_proximo_pago=fecha_expiracion
        )
        
        messages.success(request, 'Suscripción creada exitosamente')
        return redirect('suscripcion:index')
    
    negocios = Negocio.objects.all()
    planes = Plan.objects.filter(activo=True)
    
    return render(request, 'modulos/suscripcion/crear.html', {
        'negocios': negocios,
        'planes': planes
    })

@es_superadmin
def editar(request, id_suscripcion):
    suscripcion = get_object_or_404(Suscripcion, id=id_suscripcion)
    
    if request.method == 'POST':
        plan_id = request.POST['plan']
        estado = request.POST['estado']
        
        suscripcion.plan = Plan.objects.get(id=plan_id)
        suscripcion.estado = estado
        
        # Si se reactiva, actualizar fechas
        if estado == 'ACTIVA' and suscripcion.estado != 'ACTIVA':
            suscripcion.fecha_expiracion = timezone.now() + timedelta(days=suscripcion.plan.duracion_dias)
            suscripcion.fecha_ultimo_pago = timezone.now()
            suscripcion.fecha_proximo_pago = suscripcion.fecha_expiracion
        
        suscripcion.save()
        
        messages.success(request, 'Suscripción actualizada exitosamente')
        return redirect('suscripcion:index')
    
    planes = Plan.objects.filter(activo=True)
    estados = [
        ('ACTIVA', 'Activa'),
        ('INACTIVA', 'Inactiva'),
        ('VENCIDA', 'Vencida'),
        ('CANCELADA', 'Cancelada')
    ]
    
    return render(request, 'modulos/suscripcion/editar.html', {
        'suscripcion': suscripcion,
        'planes': planes,
        'estados': estados
    })

@es_superadmin
def eliminar(request, id_suscripcion):
    suscripcion = get_object_or_404(Suscripcion, id=id_suscripcion)
    
    if request.method == 'POST':
        suscripcion.delete()
        messages.success(request, 'Suscripción eliminada exitosamente')
        return redirect('suscripcion:index')
    
    return render(request, 'modulos/suscripcion/eliminar.html', {'suscripcion': suscripcion})

@es_superadmin
def renovar(request, id_suscripcion):
    suscripcion = get_object_or_404(Suscripcion, id=id_suscripcion)
    
    if request.method == 'POST':
        suscripcion.renovar()
        messages.success(request, 'Suscripción renovada exitosamente')
        return redirect('suscripcion:index')
    
    return render(request, 'modulos/suscripcion/renovar.html', {'suscripcion': suscripcion})

# CRUD para Planes
@es_superadmin
def planes_index(request):
    planes = Plan.objects.all().order_by('precio_mensual')
    return render(request, 'modulos/suscripcion/planes_index.html', {'planes': planes})

@es_superadmin
def plan_crear(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        precio_mensual = request.POST['precio_mensual']
        duracion_dias = request.POST['duracion_dias']
        max_reservas = request.POST['max_reservas']
        max_servicios = request.POST['max_servicios']
        max_horarios = request.POST['max_horarios']
        soporte_prioritario = 'soporte_prioritario' in request.POST
        estadisticas_avanzadas = 'estadisticas_avanzadas' in request.POST
        
        plan = Plan.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio_mensual=precio_mensual,
            duracion_dias=duracion_dias,
            max_reservas=max_reservas,
            max_servicios=max_servicios,
            max_horarios=max_horarios,
            soporte_prioritario=soporte_prioritario,
            estadisticas_avanzadas=estadisticas_avanzadas
        )
        
        messages.success(request, 'Plan creado exitosamente')
        return redirect('suscripcion:planes_index')
    
    return render(request, 'modulos/suscripcion/plan_crear.html')
