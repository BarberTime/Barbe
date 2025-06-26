from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.usuario.decorators import es_barbero_o_superadmin
from .models import Cliente
from apps.usuario.models import Usuario
from apps.rol.models import Rol
from apps.usuario_rol.models import UsuarioRol

@es_barbero_o_superadmin
def index(request):
    clientes = Cliente.objects.all()
    return render(request, 'modulos/cliente/index.html', {'clientes': clientes})

@es_barbero_o_superadmin
def crear(request):
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre']
            apellido = request.POST.get('apellido', '')
            telefono = request.POST['telefono']
            direccion = request.POST['direccion']
            usuario_nombre = request.POST['usuario']
            password = request.POST['password']
            
            # Crear usuario
            usuario = Usuario.objects.create(
                usuario=usuario_nombre,
                password=password
            )
            
            # Obtener rol de cliente
            rol_cliente, created = Rol.objects.get_or_create(nombre='cliente')
            
            # Crear relación usuario-rol
            UsuarioRol.objects.create(
                usuario=usuario,
                rol=rol_cliente
            )
            
            # Crear cliente
            cliente = Cliente.objects.create(
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                direccion=direccion,
                usuario=usuario,
                rol=rol_cliente
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Cliente creado exitosamente',
                'cliente': {
                    'id_cliente': str(cliente.id_cliente),
                    'nombre': cliente.nombre,
                    'apellido': cliente.apellido,
                    'telefono': cliente.telefono,
                    'direccion': cliente.direccion,
                    'usuario': cliente.usuario.usuario
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return render(request, 'modulos/cliente/crear.html')

@es_barbero_o_superadmin
def editar(request, id_cliente):
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.get(id_cliente=id_cliente)
            
            # Actualizar datos del usuario
            cliente.usuario.usuario = request.POST['usuario']
            cliente.usuario.save()
            
            # Actualizar datos del cliente
            cliente.nombre = request.POST['nombre']
            cliente.apellido = request.POST.get('apellido', '')
            cliente.telefono = request.POST['telefono']
            cliente.direccion = request.POST['direccion']
            
            cliente.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Cliente actualizado exitosamente',
                'cliente': {
                    'id_cliente': str(cliente.id_cliente),
                    'nombre': cliente.nombre,
                    'apellido': cliente.apellido,
                    'telefono': cliente.telefono,
                    'direccion': cliente.direccion,
                    'usuario': cliente.usuario.usuario
                }
            })
            
        except Cliente.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cliente no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    cliente = get_object_or_404(Cliente, id_cliente=id_cliente)
    return render(request, 'modulos/cliente/editar.html', {'cliente': cliente})

@es_barbero_o_superadmin
def eliminar(request, id_cliente):
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.get(id_cliente=id_cliente)
            usuario = cliente.usuario
            cliente.delete()
            usuario.delete()
            
            return JsonResponse({'success': True, 'message': 'Cliente eliminado exitosamente'})
        except Cliente.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cliente no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    cliente = get_object_or_404(Cliente, id_cliente=id_cliente)
    return render(request, 'modulos/cliente/eliminar.html', {'cliente': cliente})

@es_barbero_o_superadmin
def detalle(request, id_cliente):
    cliente = get_object_or_404(Cliente, id_cliente=id_cliente)
    return render(request, 'modulos/cliente/detalle.html', {'cliente': cliente})
