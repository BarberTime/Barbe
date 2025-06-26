from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.usuario.decorators import es_barbero_o_superadmin, es_superadmin
from .models import Negocio
from apps.usuario.models import Usuario

@es_superadmin
def index(request):
    # Get user from session
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        # Get only the business associated with this user
        try:
            negocio = Negocio.objects.get(usuario=usuario)
            return render(request, 'modulos/negocio/index.html', {
                'negocio': negocio,
                'usuario': usuario
            })
        except Negocio.DoesNotExist:
            messages.warning(request, 'No tienes un negocio registrado')
            return render(request, 'modulos/negocio/index.html', {
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
            nombre = request.POST['nombre']
            descripcion = request.POST['descripcion']
            departamento = request.POST['departamento']
            direccion = request.POST['direccion']
            telefono = request.POST['telefono']
            longitud = request.POST['longitud']
            latitud = request.POST['latitud']
            
            try:
                # Create business
                negocio = Negocio.objects.create(
                    nombre=nombre,
                    usuario=usuario,
                    descripcion=descripcion,
                    departamento=departamento,
                    direccion=direccion,
                    telefono=telefono,
                    longitud=longitud,
                    latitud=latitud
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Negocio creado exitosamente',
                    'negocio': {
                        'id_negocio': str(negocio.id_negocio),
                        'nombre': negocio.nombre,
                        'descripcion': negocio.descripcion,
                        'departamento': negocio.departamento,
                        'direccion': negocio.direccion,
                        'telefono': negocio.telefono,
                        'longitud': negocio.longitud,
                        'latitud': negocio.latitud,
                        'fecha_registro': negocio.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
                
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})
        
        return render(request, 'modulos/negocio/crear.html', {'usuario': usuario})
        
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Usuario no encontrado'})

@es_barbero_o_superadmin
def editar(request, id_negocio):
    if request.method == 'POST':
        try:
            negocio = Negocio.objects.get(id_negocio=id_negocio)
            
            # Update business details
            negocio.nombre = request.POST['nombre']
            negocio.descripcion = request.POST['descripcion']
            negocio.departamento = request.POST['departamento']
            negocio.direccion = request.POST['direccion']
            negocio.telefono = request.POST['telefono']
            negocio.longitud = request.POST['longitud']
            negocio.latitud = request.POST['latitud']
            negocio.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Negocio actualizado exitosamente',
                'negocio': {
                    'id_negocio': str(negocio.id_negocio),
                    'nombre': negocio.nombre,
                    'descripcion': negocio.descripcion,
                    'departamento': negocio.departamento,
                    'direccion': negocio.direccion,
                    'telefono': negocio.telefono,
                    'longitud': negocio.longitud,
                    'latitud': negocio.latitud,
                    'fecha_registro': negocio.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            
        except Negocio.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Negocio no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    negocio = get_object_or_404(Negocio, id_negocio=id_negocio)
    return render(request, 'modulos/negocio/editar.html', {'negocio': negocio})

@es_superadmin
def eliminar(request, id_negocio):
    if request.method == 'POST':
        try:
            negocio = Negocio.objects.get(id_negocio=id_negocio)
            negocio.delete()
            return JsonResponse({'success': True, 'message': 'Negocio eliminado exitosamente'})
        except Negocio.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Negocio no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    negocio = get_object_or_404(Negocio, id_negocio=id_negocio)
    return render(request, 'modulos/negocio/eliminar.html', {'negocio': negocio})

@es_barbero_o_superadmin
def detalle(request, id_negocio):
    negocio = get_object_or_404(Negocio, id_negocio=id_negocio)
    
    # Get user from session
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        # Check permissions
        if hasattr(usuario, 'negocio') and negocio != usuario.negocio:
            messages.error(request, 'No tienes permisos para ver este negocio')
            return redirect('negocio:index')
        
        return render(request, 'modulos/negocio/detalle.html', {
            'negocio': negocio,
            'usuario': usuario
        })
    except Usuario.DoesNotExist:
        return redirect('web:login')
