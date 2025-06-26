from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.usuario.decorators import es_barbero_o_superadmin
from .models import Empleado
from apps.negocio.models import Negocio
from apps.rol.models import Rol
from apps.usuario.models import Usuario
from apps.usuario_rol.models import UsuarioRol

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
            # Show only employees of this business
            empleados = Empleado.objects.filter(negocio=negocio)
            return render(request, 'modulos/empleado/index.html', {
                'empleados': empleados,
                'usuario': usuario,
                'negocio': negocio
            })
        except Negocio.DoesNotExist:
            # Si no tiene negocio propio, mostrar todos los empleados (para superadmin)
            empleados = Empleado.objects.all()
            return render(request, 'modulos/empleado/index.html', {
                'empleados': empleados,
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
                # Verificar si el usuario ya existe
                if Usuario.objects.filter(usuario=request.POST['usuario']).exists():
                    messages.error(request, 'El nombre de usuario ya existe')
                    return redirect('empleado:crear')
                
                # Obtener el negocio - intentamos primero obtener el negocio del usuario actual
                try:
                    negocio = Negocio.objects.get(usuario=usuario)
                except Negocio.DoesNotExist:
                    # Si no tiene negocio propio, debe seleccionar uno (para superadmin)
                    if 'negocio' not in request.POST or not request.POST['negocio']:
                        messages.error(request, 'Debe seleccionar un negocio')
                        return redirect('empleado:crear')
                    negocio = Negocio.objects.get(id_negocio=request.POST['negocio'])
                
                # Crear Usuario - usando solo los campos que existen en el modelo
                nuevo_usuario = Usuario(
                    usuario=request.POST['usuario'],
                    password=request.POST['password']
                )
                # Solo establecer tipo_usuario si el campo existe
                if hasattr(Usuario, 'tipo_usuario'):
                    nuevo_usuario.tipo_usuario = 'EMPLEADO'
                nuevo_usuario.save()

                # Crear Empleado con todos los campos
                empleado = Empleado(
                    nombre=request.POST['nombre'],
                    apellido=request.POST['apellido'], 
                    telefono=request.POST['telefono'],
                    usuario=nuevo_usuario,
                    negocio=negocio,
                    especialidad=request.POST['especialidad'],
                    experiencia_anios=request.POST['experiencia_anios']
                )
                
                # Manejar la foto de perfil si se subió
                if 'foto_perfil' in request.FILES:
                    empleado.foto_perfil = request.FILES['foto_perfil']
                
                empleado.save()
                
                messages.success(request, 'Empleado creado exitosamente')
                return redirect('empleado:index')
                
            except Exception as e:
                messages.error(request, f'Error al crear empleado: {str(e)}')
                return redirect('empleado:crear')
        
        # GET - Mostrar formulario
        # Verificar si el usuario tiene un negocio propio
        try:
            negocio_actual = Negocio.objects.get(usuario=usuario)
            # Es barbero/dueño de negocio
            return render(request, 'modulos/empleado/crear.html', {
                'es_barbero': True,
                'negocio_actual': negocio_actual
            })
        except Negocio.DoesNotExist:
            # Es superadmin o no tiene negocio propio
            negocios = Negocio.objects.all()
            return render(request, 'modulos/empleado/crear.html', {
                'es_barbero': False,
                'negocios': negocios
            })
            
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('web:login')

@es_barbero_o_superadmin
def editar(request, id_empleado):
    empleado = get_object_or_404(Empleado, id_empleado=id_empleado)
    
    if request.method == 'POST':
        try:
            # Verificar si el usuario ya existe (excluyendo el actual)
            if Usuario.objects.filter(usuario=request.POST['usuario']).exclude(id_usuario=empleado.usuario.id_usuario).exists():
                messages.error(request, 'El nombre de usuario ya existe')
                return redirect('empleado:editar', id_empleado=id_empleado)
            
            # Actualizar datos del usuario (solo campos que existen)
            empleado.usuario.usuario = request.POST['usuario']

            # Solo actualizar la contraseña si se proporciona
            if request.POST.get('password'):
                empleado.usuario.password = request.POST['password']

            empleado.usuario.save()

            # Actualizar datos del empleado (aquí están los campos nombre, apellido, telefono)
            empleado.nombre = request.POST['nombre']
            empleado.apellido = request.POST['apellido']
            empleado.telefono = request.POST['telefono']
            empleado.especialidad = request.POST['especialidad']
            empleado.experiencia_anios = request.POST['experiencia_anios']
            
            # Manejar la foto de perfil si se subió una nueva
            if 'foto_perfil' in request.FILES:
                empleado.foto_perfil = request.FILES['foto_perfil']
            
            empleado.save()
            
            messages.success(request, 'Empleado actualizado exitosamente')
            return redirect('empleado:index')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar empleado: {str(e)}')
            return redirect('empleado:editar', id_empleado=id_empleado)
    
    return render(request, 'modulos/empleado/editar.html', {'empleado': empleado})

@es_barbero_o_superadmin
def eliminar(request, id_empleado):
    empleado = get_object_or_404(Empleado, id_empleado=id_empleado)
    
    if request.method == 'POST':
        try:
            nombre_completo = f"{empleado.nombre} {empleado.apellido}"
            empleado.delete()
            messages.success(request, f'Empleado {nombre_completo} eliminado exitosamente')
            return redirect('empleado:index')
        except Exception as e:
            messages.error(request, f'Error al eliminar empleado: {str(e)}')
            return redirect('empleado:eliminar', id_empleado=id_empleado)
    
    return render(request, 'modulos/empleado/eliminar.html', {'empleado': empleado})
