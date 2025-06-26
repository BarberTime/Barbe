from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Reserva
from apps.negocio.models import Negocio
from apps.cliente.models import Cliente
from apps.servicio.models import Servicio
from apps.empleado.models import Empleado
from apps.web.decorators import es_barbero_o_superadmin, es_empleado
from datetime import datetime, date
from apps.usuario.models import Usuario
from decimal import Decimal

@es_barbero_o_superadmin
def index(request):
    # Get user from session
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        # Get the business associated with this user
        try:
            negocio = Negocio.objects.get(usuario=usuario)
            reservas = Reserva.objects.filter(negocio=negocio).prefetch_related('servicios')
            return render(request, 'modulos/reserva/index.html', {
                'reservas': reservas,
                'usuario': usuario,
                'negocio': negocio
            })
        except Negocio.DoesNotExist:
            messages.warning(request, 'No tienes un negocio registrado')
            return render(request, 'modulos/reserva/index.html', {
                'usuario': usuario
            })
    except Usuario.DoesNotExist:
        return redirect('web:login')

@es_barbero_o_superadmin
def crear(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, 'Usuario no autenticado')
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        if request.method == 'POST':
            try:
                cliente_id = request.POST['cliente']
                servicios_ids = request.POST.getlist('servicios')  # Obtener múltiples servicios
                empleado_id = request.POST.get('empleado')
                fecha = request.POST['fecha']
                hora = request.POST['hora']
                estado = 'pendiente'
                
                if not servicios_ids:
                    messages.error(request, 'Debe seleccionar al menos un servicio')
                    raise ValueError('No services selected')
                
                cliente = Cliente.objects.get(id_cliente=cliente_id)
                servicios = Servicio.objects.filter(id_servicio__in=servicios_ids)
                
                if empleado_id:
                    empleado = Empleado.objects.get(id_empleado=empleado_id)
                else:
                    empleado = None
                
                # Get the business associated with this user
                if hasattr(usuario, 'negocio'):
                    negocio = usuario.negocio
                else:
                    # Get negocio from the first service
                    negocio = servicios.first().negocio
                
                # Calculate total
                total = sum(servicio.precio for servicio in servicios)
                
                # Create reservation
                reserva = Reserva.objects.create(
                    negocio=negocio,
                    cliente=cliente,
                    empleado=empleado,
                    fecha=fecha,
                    hora=hora,
                    estado=estado,
                    total=total
                )
                
                # Add services to the reservation
                reserva.servicios.set(servicios)
                
                messages.success(request, 'Reserva creada exitosamente')
                return redirect('reserva:index')
                
            except (Cliente.DoesNotExist, Servicio.DoesNotExist, Empleado.DoesNotExist):
                messages.error(request, 'Datos inválidos seleccionados')
            except Exception as e:
                messages.error(request, f'Error al crear la reserva: {str(e)}')
        
        # For GET request, show the form
        try:
            if hasattr(usuario, 'negocio'):
                negocio = usuario.negocio
                clientes = Cliente.objects.all()
                servicios = Servicio.objects.filter(negocio=negocio)
                empleados = Empleado.objects.filter(negocio=negocio, activo=True)
            else:
                clientes = Cliente.objects.all()
                servicios = Servicio.objects.all()
                empleados = Empleado.objects.filter(activo=True)
            
            return render(request, 'modulos/reserva/crear.html', {
                'clientes': clientes,
                'servicios': servicios,
                'empleados': empleados,
                'usuario': usuario
            })
        except Exception as e:
            messages.error(request, f'Error al cargar el formulario: {str(e)}')
            return redirect('reserva:index')
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('web:login')

@es_barbero_o_superadmin
def editar(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
    
    if request.method == 'POST':
        try:

            reserva.fecha = request.POST['fecha']
            reserva.hora = request.POST['hora']
            reserva.estado = request.POST['estado']
            
            
            servicios_ids = request.POST.getlist('servicios')
            if servicios_ids:
                servicios = Servicio.objects.filter(id_servicio__in=servicios_ids)
                reserva.servicios.set(servicios)
            
                reserva.total = sum(servicio.precio for servicio in servicios)
            
            empleado_id = request.POST.get('empleado')
            if empleado_id:
                reserva.empleado = Empleado.objects.get(id_empleado=empleado_id)
            else:
                reserva.empleado = None
            
            reserva.save()
            
            messages.success(request, 'Reserva actualizada exitosamente')
            return redirect('reserva:index')
            
        except Empleado.DoesNotExist:
            messages.error(request, 'Empleado seleccionado no válido')
        except Exception as e:
            messages.error(request, f'Error al actualizar la reserva: {str(e)}')
    
    
    try:
        empleados = Empleado.objects.filter(negocio=reserva.negocio, activo=True)
        servicios = Servicio.objects.filter(negocio=reserva.negocio)
    except:
        empleados = Empleado.objects.filter(activo=True)
        servicios = Servicio.objects.all()
    
    
    estados = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]
    
    return render(request, 'modulos/reserva/editar.html', {
        'reserva': reserva,
        'empleados': empleados,
        'servicios': servicios,
        'estados': estados
    })

@es_barbero_o_superadmin
def cambiar_estado(request, id_reserva):
    """Vista para cambiar solo el estado de una reserva desde el calendario"""
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
    
    if request.method == 'POST':
        try:
            nuevo_estado = request.POST.get('estado')
            if nuevo_estado in ['pendiente', 'confirmada', 'cancelada', 'completada']:
                reserva.estado = nuevo_estado
                reserva.save()
                messages.success(request, f'Estado de la reserva cambiado a {nuevo_estado}')
            else:
                messages.error(request, 'Estado no válido')
        except Exception as e:
            messages.error(request, f'Error al cambiar el estado: {str(e)}')
        
        # Redirigir de vuelta al calendario
        return redirect('reserva:calendario')
    
    # Si es GET, redirigir al calendario
    return redirect('reserva:calendario')

@es_barbero_o_superadmin
def eliminar(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
    
    if request.method == 'POST':
        try:
            reserva.delete()
            messages.success(request, 'Reserva eliminada exitosamente')
            return redirect('reserva:index')
        except Exception as e:
            messages.error(request, f'Error al eliminar la reserva: {str(e)}')
            return redirect('reserva:index')
    
    return render(request, 'modulos/reserva/eliminar.html', {'reserva': reserva})

@es_barbero_o_superadmin
def calendario(request):
    # Get user from session
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        # Get the business associated with this user
        try:
            negocio = Negocio.objects.get(usuario=usuario)
            reservas = Reserva.objects.filter(negocio=negocio).prefetch_related('servicios')
        except Negocio.DoesNotExist:
            # If superadmin, show all reservations
            reservas = Reserva.objects.all().prefetch_related('servicios')
        
        # Convert reservations to JSON format for the calendar
        eventos = []
        for reserva in reservas:
            color = {
                'pendiente': '#FCD34D',
                'confirmada': '#10B981',
                'cancelada': '#EF4444',
                'completada': '#6B7280'
            }.get(reserva.estado, '#6B7280')
            
            servicios_nombres = ', '.join([servicio.nombre for servicio in reserva.servicios.all()])
            
            eventos.append({
                'id': str(reserva.id_reserva),
                'title': f'Reserva #{str(reserva.id_reserva)[:8]}',
                'start': reserva.fecha.strftime('%Y-%m-%d'),
                'end': reserva.fecha.strftime('%Y-%m-%d'),
                'color': color,
                'extendedProps': {
                    'cliente': f'{reserva.cliente.nombre} {reserva.cliente.apellido}',
                    'servicios': servicios_nombres,
                    'empleado': f'{reserva.empleado.nombre} {reserva.empleado.apellido}' if reserva.empleado else 'Sin asignar',
                    'estado': reserva.estado,
                    'hora': reserva.hora.strftime('%H:%M') if reserva.hora else '',
                    'total': str(reserva.total),
                    'telefono': reserva.cliente.telefono if hasattr(reserva.cliente, 'telefono') else ''
                }
            })
        
        return render(request, 'modulos/reserva/calendario.html', {
            'eventos': eventos,
            'usuario': usuario
        })
    except Usuario.DoesNotExist:
        return redirect('web:login')

@es_empleado
def calendario_empleado(request):
    try:
        # Get user from session
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return redirect('web:login')
        
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        empleado = Empleado.objects.get(usuario=usuario)
        reservas = Reserva.objects.filter(empleado=empleado).prefetch_related('servicios')
        
        # Convert reservations to JSON format for the calendar
        eventos = []
        for reserva in reservas:
            color = {
                'pendiente': '#FCD34D',
                'confirmada': '#10B981',
                'cancelada': '#EF4444',
                'completada': '#6B7280'
            }.get(reserva.estado, '#6B7280')
            
            servicios_nombres = ', '.join([servicio.nombre for servicio in reserva.servicios.all()])
            
            eventos.append({
                'id': str(reserva.id_reserva),
                'title': f"{reserva.cliente.nombre} - {servicios_nombres}",
                'start': f"{reserva.fecha}T{reserva.hora}",
                'backgroundColor': color,
                'borderColor': color,
                'extendedProps': {
                    'cliente': reserva.cliente.nombre,
                    'servicios': servicios_nombres,
                    'estado': reserva.get_estado_display(),
                    'total': str(reserva.total),
                    'telefono': reserva.cliente.telefono if hasattr(reserva.cliente, 'telefono') else ''
                }
            })
        
        return render(request, 'modulos/reserva/calendario_empleado.html', {
            'eventos': eventos
        })
        
    except (Empleado.DoesNotExist, Usuario.DoesNotExist):
        messages.error(request, 'No se pudo acceder al calendario')
        return redirect('web:dashboard_empleado')
