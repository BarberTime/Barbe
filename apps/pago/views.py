from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Pago
from apps.reserva.models import Reserva
from apps.web.decorators import es_barbero_o_superadmin, es_superadmin
from apps.usuario.models import Usuario

@es_barbero_o_superadmin
def index(request):
    # Get user from session
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        if hasattr(usuario, 'negocio'):
            # Get payments for reservations from the user's business
            reservas_negocio = Reserva.objects.filter(negocio=usuario.negocio)
            pagos = Pago.objects.filter(reserva__in=reservas_negocio).order_by('-fecha_pago')
        else:
            pagos = Pago.objects.all().order_by('-fecha_pago')
        
        return render(request, 'modulos/pago/index.html', {
            'pagos': pagos,
            'usuario': usuario
        })
    except Usuario.DoesNotExist:
        return redirect('web:login')

@es_barbero_o_superadmin
def crear(request):
    # Get user from session
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'success': False, 'message': 'Usuario no autenticado'})
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        if request.method == 'POST':
            reserva_id = request.POST['reserva']
            metodo_pago = request.POST['metodo_pago']
            monto = request.POST['monto']
            
            reserva = Reserva.objects.get(id_reserva=reserva_id)
            
            # Check permissions
            if hasattr(usuario, 'negocio') and reserva.negocio != usuario.negocio:
                return JsonResponse({'success': False, 'message': 'No tienes permisos para registrar pagos para este negocio'})
            
            pago = Pago.objects.create(
                reserva=reserva,
                metodo_pago=metodo_pago,
                monto=monto
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Pago registrado exitosamente',
                'pago': {
                    'id_pago': str(pago.id_pago),
                    'cliente_nombre': pago.reserva.cliente.nombre,
                    'cliente_apellido': pago.reserva.cliente.apellido,
                    'servicio_nombre': pago.reserva.servicio.nombre,
                    'monto': str(pago.monto),
                    'metodo_pago': pago.metodo_pago,
                    'fecha_pago': pago.fecha_pago.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            
        # For GET, return the form HTML
        if hasattr(usuario, 'negocio'):
            reservas = Reserva.objects.filter(negocio=usuario.negocio)
        else:
            reservas = Reserva.objects.all()
            
        return render(request, 'modulos/pago/crear.html', {
            'reservas': reservas,
            'usuario': usuario
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@es_barbero_o_superadmin
def editar(request, id_pago):
    if request.method == 'POST':
        try:
            pago = Pago.objects.get(id_pago=id_pago)
            
            # Update payment details
            pago.metodo_pago = request.POST['metodo_pago']
            pago.monto = request.POST['monto']
            pago.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Pago actualizado exitosamente',
                'pago': {
                    'id_pago': str(pago.id_pago),
                    'cliente_nombre': pago.reserva.cliente.nombre,
                    'cliente_apellido': pago.reserva.cliente.apellido,
                    'servicio_nombre': pago.reserva.servicio.nombre,
                    'monto': str(pago.monto),
                    'metodo_pago': pago.metodo_pago,
                    'fecha_pago': pago.fecha_pago.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            
        except Pago.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pago no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    # For GET, return the form HTML
    pago = get_object_or_404(Pago, id_pago=id_pago)
    return render(request, 'modulos/pago/editar.html', {'pago': pago})

@es_barbero_o_superadmin
def eliminar(request, id_pago):
    if request.method == 'POST':
        try:
            pago = Pago.objects.get(id_pago=id_pago)
            pago.delete()
            return JsonResponse({'success': True, 'message': 'Pago eliminado exitosamente'})
        except Pago.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pago no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    pago = get_object_or_404(Pago, id_pago=id_pago)
    return render(request, 'modulos/pago/eliminar.html', {'pago': pago})

@es_barbero_o_superadmin
def detalle(request, id_pago):
    pago = get_object_or_404(Pago, id_pago=id_pago)
    
    # Get user from session
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        # Check permissions
        if hasattr(usuario, 'negocio') and pago.reserva.negocio != usuario.negocio:
            messages.error(request, 'No tienes permisos para ver este pago')
            return redirect('pago:index')
        
        return render(request, 'modulos/pago/detalle.html', {
            'pago': pago,
            'usuario': usuario
        })
    except Usuario.DoesNotExist:
        return redirect('web:login')
