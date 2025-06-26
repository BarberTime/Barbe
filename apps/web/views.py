from django.shortcuts import render, redirect, get_object_or_404
from apps.negocio.models import Negocio
from apps.servicio.models import Servicio
from apps.empleado.models import Empleado
from apps.horario.models import Horario
from apps.cliente.models import Cliente
from apps.reserva.models import Reserva
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from datetime import datetime, timedelta
from apps.usuario.models import Usuario
from apps.usuario_rol.models import UsuarioRol
from apps.suscripcion.models import Suscripcion
from .decorators import es_superadmin, es_barbero, es_empleado, cualquier_rol_admin
from apps.usuario.decorators import es_barbero_o_superadmin
from apps.rol.models import Rol
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import json
import uuid

class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

# Vista principal
def index(request):
    # Obtener todos los negocios ordenados por fecha
    negocios_destacados = Negocio.objects.all().order_by('-fecha_registro')
    
    # Obtener reservas del cliente si está logueado
    reservas_cliente = []
    cliente = None
    if request.session.get('cliente_id'):
        try:
            cliente = Cliente.objects.get(id_cliente=request.session['cliente_id'])
            reservas_cliente = Reserva.objects.filter(cliente=cliente).order_by('-fecha', '-hora')
        except Cliente.DoesNotExist:
            pass
    
    contexto = {
        'negocios_destacados': negocios_destacados,
        'reservas_cliente': reservas_cliente,
        'cliente': cliente
    }
    
    return render(request, 'index.html', contexto)

def detalle_negocio(request, negocio_id):
    # Obtener el negocio específico
    negocio = get_object_or_404(Negocio, id_negocio=negocio_id)
    
    # Obtener todos los datos relacionados para este negocio
    servicios = Servicio.objects.filter(negocio=negocio)
    empleados = Empleado.objects.filter(negocio=negocio)
    horarios = Horario.objects.filter(negocio=negocio)
    
    # Obtener reservas del cliente si está logueado
    reservas_cliente = []
    if request.session.get('cliente_id'):
        try:
            cliente = Cliente.objects.get(id_cliente=request.session['cliente_id'])
            reservas_cliente = Reserva.objects.filter(cliente=cliente).order_by('-fecha', '-hora')
        except Cliente.DoesNotExist:
            pass
    
    # Pasar todos los datos al template
    contexto = {
        'negocio': negocio,
        'servicios': servicios,
        'empleados': empleados,
        'horarios': horarios,
        'reservas_cliente': reservas_cliente
    }
    
    return render(request, 'bussines-detail.html', contexto)

def iniciar_sesion_cliente(request):
    if request.method == 'POST':
        nombre_usuario = request.POST['usuario']
        contrasena = request.POST['password']
        siguiente_url = request.POST.get('next', '/')
        
        try:
            # Buscar el usuario en nuestra base de datos
            usuario = Usuario.objects.get(usuario=nombre_usuario)
            
            # Verificar la contraseña
            if usuario.password == contrasena:
                # Verificar si es cliente
                try:
                    cliente = Cliente.objects.get(usuario=usuario)
                    # Crear sesión para cliente
                    request.session['cliente_id'] = str(cliente.id_cliente)
                    request.session['cliente_nombre'] = cliente.nombre
                    request.session['usuario_id'] = str(usuario.id_usuario)
                    
                    messages.success(request, f'Bienvenido {cliente.nombre}')
                    return redirect(siguiente_url)
                    
                except Cliente.DoesNotExist:
                    messages.error(request, 'Este usuario no es un cliente')
            else:
                messages.error(request, 'Contraseña incorrecta')
                
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
    
    # Si hay error, redirigir de vuelta
    return redirect(request.META.get('HTTP_REFERER', '/'))

def registrar_cliente(request):
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre']
            apellido = request.POST.get('apellido', '')
            nombre_usuario = request.POST['usuario']
            contrasena = request.POST['password']
            telefono = request.POST['telefono']
            direccion = request.POST['direccion']
            siguiente_url = request.POST.get('next', '/')
            
            # Verificar si el usuario ya existe
            if Usuario.objects.filter(usuario=nombre_usuario).exists():
                messages.error(request, 'El usuario ya existe')
                return redirect(request.META.get('HTTP_REFERER', '/'))
            
            # Crear usuario
            usuario = Usuario.objects.create(
                usuario=nombre_usuario,
                password=contrasena
            )
            
            # Obtener o crear rol de cliente
            rol_cliente, creado = Rol.objects.get_or_create(nombre='Cliente')
            
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
            
            # Crear sesión automáticamente
            request.session['cliente_id'] = str(cliente.id_cliente)
            request.session['cliente_nombre'] = cliente.nombre
            request.session['usuario_id'] = str(usuario.id_usuario)
            
            messages.success(request, f'Cuenta creada exitosamente. Bienvenido {cliente.nombre}')
            return redirect(siguiente_url)
            
        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

def cerrar_sesion_cliente(request):
    # Limpiar sesión de cliente
    if 'cliente_id' in request.session:
        del request.session['cliente_id']
    if 'cliente_nombre' in request.session:
        del request.session['cliente_nombre']
    if 'usuario_id' in request.session:
        del request.session['usuario_id']
    
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('web:index')

def registrar_negocio(request):
    if request.method == 'POST':
        try:
            # Datos del usuario
            nombre_usuario = request.POST['usuario']
            contrasena = request.POST['password']
            
            # Datos del negocio
            nombre = request.POST['nombre']
            descripcion = request.POST['descripcion']
            departamento = request.POST['departamento']
            direccion = request.POST['direccion']
            telefono = request.POST['telefono']
            latitud = request.POST['latitud']
            longitud = request.POST['longitud']
            logo = request.FILES.get('logo')
            foto = request.FILES.get('foto')
            
            # Verificar si el usuario ya existe
            if Usuario.objects.filter(usuario=nombre_usuario).exists():
                messages.error(request, 'El usuario ya existe')
                return redirect('web:index')
            
            # Crear usuario
            usuario = Usuario.objects.create(
                usuario=nombre_usuario,
                password=contrasena
            )
            
            # Obtener o crear rol de barbero
            rol_barbero, creado = Rol.objects.get_or_create(nombre='Barbero')
            
            # Crear relación usuario-rol
            UsuarioRol.objects.create(
                usuario=usuario,
                rol=rol_barbero
            )
            
            # Crear negocio
            negocio = Negocio.objects.create(
                nombre=nombre,
                usuario=usuario,
                descripcion=descripcion,
                departamento=departamento,
                direccion=direccion,
                telefono=telefono,
                latitud=latitud,
                longitud=longitud,
                logo=logo,
                foto=foto
            )
            
            messages.success(request, 'Negocio registrado exitosamente. Ahora puedes iniciar sesión.')
            return redirect('web:login')
            
        except Exception as e:
            messages.error(request, f'Error al registrar el negocio: {str(e)}')
    
    return redirect('web:index')

def crear_reserva(request):
    if request.method == 'POST':
        try:
            # Verificar si el cliente está logueado
            cliente_id = request.session.get('cliente_id')
            if not cliente_id:
                messages.error(request, 'Debes iniciar sesión para hacer una reserva')
                return redirect('web:iniciar_sesion_cliente')
            
            cliente = Cliente.objects.get(id_cliente=cliente_id)
            negocio_id = request.POST['negocio_id']
            servicios_ids = request.POST['servicios_ids'].split(',')
            empleado_id = request.POST.get('empleado_id')
            fecha = request.POST['fecha']
            hora = request.POST['hora']
            
            # Validar formato de hora
            try:
                from datetime import datetime
                # Intentar parsear la hora para validar el formato
                # Aceptar tanto HH:MM como HH:MM:SS
                if len(hora.split(':')) == 2:
                    # Si solo tiene HH:MM, agregar :00 para los segundos
                    hora = hora + ':00'
                datetime.strptime(hora, '%H:%M:%S')
            except ValueError:
                messages.error(request, 'Formato de hora inválido. Use formato HH:MM')
                return redirect('web:detalle_negocio', negocio_id=negocio_id)
            
            # Verificar disponibilidad del empleado
            if empleado_id:
                existing_reserva = Reserva.objects.filter(
                    empleado_id=empleado_id,
                    fecha=fecha,
                    hora=hora,
                    estado__in=['pendiente', 'confirmada']
                ).exists()
                
                if existing_reserva:
                    messages.error(request, 'Este empleado ya tiene una cita programada para esa fecha y hora')
                    return redirect('web:detalle_negocio', negocio_id=negocio_id)
            
            # Obtener objetos
            negocio = Negocio.objects.get(id_negocio=negocio_id)
            servicios = Servicio.objects.filter(id_servicio__in=servicios_ids)
            empleado = None
            if empleado_id:
                empleado = Empleado.objects.get(id_empleado=empleado_id)
            
            # Calcular total
            total = sum(servicio.precio for servicio in servicios)
            
            # Crear reserva
            reserva = Reserva.objects.create(
                negocio=negocio,
                cliente=cliente,
                empleado=empleado,
                fecha=fecha,
                hora=hora,
                estado='pendiente',
                total=total
            )
            
            # Agregar servicios
            reserva.servicios.set(servicios)
            
            messages.success(request, 'Reserva creada exitosamente')
            return redirect('web:detalle_negocio', negocio_id=negocio_id)
            
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado')
        except Negocio.DoesNotExist:
            messages.error(request, 'Negocio no encontrado')
        except Servicio.DoesNotExist:
            messages.error(request, 'Uno o más servicios no encontrados')
        except Exception as e:
            messages.error(request, f'Error al crear la reserva: {str(e)}')
            
        return redirect('web:detalle_negocio', negocio_id=request.POST.get('negocio_id'))
    
    return redirect('web:index')

def iniciar_sesion(request):
    if request.method == 'POST':
        nombre_usuario = request.POST['nombre_usuario']
        contrasena = request.POST['contrasena']
        
        try:
            # Buscar el usuario en nuestra base de datos
            usuario = Usuario.objects.get(usuario=nombre_usuario)
            
            # Verificar la contraseña
            if usuario.password == contrasena:  # Aquí deberías implementar una verificación más segura
                # Crear sesión manualmente
                request.session['usuario_id'] = str(usuario.id_usuario)
                request.session['usuario_nombre'] = usuario.usuario
                
                # Verificar si el usuario existe en UsuarioRol
                try:
                    usuario_rol = UsuarioRol.objects.filter(usuario=usuario).first()
                    if usuario_rol and usuario_rol.rol:
                        nombre_rol = usuario_rol.rol.nombre.lower()
                        
                        if nombre_rol == 'superadmin':
                            return redirect('web:dashboard_superadmin')
                        elif nombre_rol == 'barbero':
                            return redirect('web:dashboard_barbero')
                        elif nombre_rol == 'empleado':
                            return redirect('web:dashboard_empleado')
                        else:
                            return redirect('web:dashboard')
                    else:
                        messages.error(request, 'No se encontró un rol asignado para este usuario')
                except UsuarioRol.DoesNotExist:
                    messages.error(request, 'El usuario no está registrado en la tabla UsuarioRol')
                
            else:
                messages.error(request, 'Contraseña incorrecta')
                
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
            
    return render(request, 'auth/login.html')

@login_required
def cerrar_sesion(request):
    if request.method == 'POST':
        logout(request)
        return redirect('web:login')
    
    return redirect('web:login')

@login_required
def dashboard(request):
    try:
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return redirect('web:login')
        
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        usuario_rol = UsuarioRol.objects.get(usuario=usuario)
        nombre_rol = usuario_rol.rol.nombre.lower()
        
        if nombre_rol == 'superadmin':
            return redirect('web:dashboard_superadmin')
        elif nombre_rol == 'barbero':
            return redirect('web:dashboard_barbero')
        elif nombre_rol == 'empleado':
            return redirect('web:dashboard_empleado')
    except UsuarioRol.DoesNotExist:
        messages.error(request, 'Usuario sin rol asignado')
        return redirect('web:iniciar_sesion')
    
    return render(request, 'dashboard/base.html')

@es_superadmin
def dashboard_superadmin(request):
    # Obtener usuario de la sesión
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        # Estadísticas generales
        total_negocios = Negocio.objects.count()
        total_reservas = Reserva.objects.count()
        total_empleados = Empleado.objects.count()
        total_servicios = Servicio.objects.count()
        
        # Reservas por mes
        hoy = datetime.now()
        hace_6_meses = hoy - timedelta(days=180)
        reservas_por_mes = Reserva.objects.filter(
            fecha_registro__gte=hace_6_meses
        ).extra(
            select={'mes': "DATE_FORMAT(fecha_registro, '%%Y-%%m')"}
        ).values('mes').annotate(total=Count('id_reserva')).order_by('mes')
        
        # Negocios más activos
        negocios_activos = Negocio.objects.annotate(
            total_reservas=Count('reserva')
        ).order_by('-total_reservas')[:5]
        
        # Obtener todos los negocios
        all_negocios = Negocio.objects.all().order_by('nombre')
        
        # Suscripciones activas
        suscripciones_activas = Suscripcion.objects.filter(estado='ACTIVA').count()
        
        contexto = {
            'total_negocios': total_negocios,
            'total_reservas': total_reservas,
            'total_empleados': total_empleados,
            'total_servicios': total_servicios,
            'reservas_por_mes': reservas_por_mes,
            'negocios_activos': negocios_activos,
            'all_negocios': all_negocios,
            'suscripciones_activas': suscripciones_activas,
            'rol': 'superadmin',
            'usuario': usuario
        }
        
        return render(request, 'dashboard/superadmin.html', contexto)
    except Usuario.DoesNotExist:
        return redirect('web:login')

@es_barbero
def dashboard_barbero(request):
    # Obtener usuario de la sesión
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        # Obtener el negocio asociado con este usuario
        try:
            # Buscamos un negocio donde el campo usuario coincida con nuestro usuario
            negocio = Negocio.objects.get(usuario=usuario)
        except Negocio.DoesNotExist:
            messages.error(request, 'No tienes un negocio asociado')
            return redirect('web:dashboard')
        
        # Estadísticas para el negocio
        total_reservas = Reserva.objects.filter(negocio=negocio).count()
        total_empleados = Empleado.objects.filter(negocio=negocio).count()
        total_servicios = Servicio.objects.filter(negocio=negocio).count()
        
        # Reservas por mes para este negocio
        hoy = datetime.now()
        hace_6_meses = hoy - timedelta(days=180)
        reservas_por_mes = Reserva.objects.filter(
            negocio=negocio,
            fecha_registro__gte=hace_6_meses
        ).extra(
            select={'mes': "DATE_FORMAT(fecha_registro, '%%Y-%%m')"}
        ).values('mes').annotate(total=Count('id_reserva')).order_by('mes')
        
        contexto = {
            'total_reservas': total_reservas,
            'total_empleados': total_empleados,
            'total_servicios': total_servicios,
            'reservas_por_mes': reservas_por_mes,
            'negocio': negocio,
            'rol': 'barbero',
            'usuario': usuario
        }
        
        return render(request, 'dashboard/barbero.html', contexto)
    except Usuario.DoesNotExist:
        return redirect('web:login')

@es_empleado
def dashboard_empleado(request):
    # Obtener usuario de la sesión
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        # Obtener el empleado
        empleado = Empleado.objects.get(usuario=usuario)
        negocio = empleado.negocio
        
        # Reservas asignadas al empleado para hoy
        hoy = datetime.now().date()
        mis_reservas_hoy = Reserva.objects.filter(
            empleado=empleado,
            fecha=hoy
        ).order_by('hora')
        
        # Próximas reservas
        proximas_reservas = Reserva.objects.filter(
            empleado=empleado,
            fecha__gte=hoy
        ).order_by('fecha', 'hora')[:5]
        
        # Servicios del negocio
        servicios = Servicio.objects.filter(negocio=negocio)
        
        contexto = {
            'empleado': empleado,
            'negocio': negocio,
            'mis_reservas_hoy': mis_reservas_hoy,
            'proximas_reservas': proximas_reservas,
            'servicios': servicios,
            'rol': 'empleado',
            'usuario': usuario
        }
        
        return render(request, 'dashboard/empleado.html', contexto)
    except Empleado.DoesNotExist:
        messages.error(request, 'No se encontró el empleado asociado')
        contexto = {'rol': 'empleado'}
    except Exception as e:
        messages.error(request, f'Error inesperado: {str(e)}')
        contexto = {'rol': 'empleado'}
    
    return render(request, 'dashboard/empleado.html', contexto)

@login_required
def perfil(request):
    # Obtener el usuario de la sesión
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, 'No estás autenticado')
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        roles = UsuarioRol.objects.filter(usuario=usuario)
        
        contexto = {
            'usuario': usuario,
            'roles': roles
        }
        return render(request, 'perfil.html', contexto)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('web:login')

@es_superadmin
def superadmin_negocio(request):
    # Obtener todos los negocios
    negocios = Negocio.objects.all().order_by('nombre')
    
    contexto = {
        'negocios': negocios,
        'rol': 'superadmin',
        'usuario': request.session.get('usuario_id')
    }
    
    return render(request, 'dashboard/superadmin_negocio.html', contexto)

@es_superadmin
def superadmin_usuario(request):
    # Get the BARBERO role from the database
    rol_barbero = Rol.objects.get(nombre='Barbero')
    
    # Get all users with BARBERO role through UsuarioRol
    usuarios = UsuarioRol.objects.filter(
        rol=rol_barbero
    ).order_by('usuario')
    
    contexto = {
        'usuarios': usuarios,
        'rol': 'superadmin',
        'usuario': request.session.get('usuario_id')
    }
    
    return render(request, 'modulos/usuario/index.html', contexto)

@es_superadmin
def superadmin_suscripcion(request):
    # Obtener todas las suscripciones
    suscripciones = Suscripcion.objects.all().order_by('-fecha_inicio')
    
    contexto = {
        'suscripciones': suscripciones,
        'rol': 'superadmin',
        'usuario': request.session.get('usuario_id')
    }
    
    return render(request, 'modulos/suscripcion/index.html', contexto)

@es_superadmin
def superadmin_suscripcion_editar(request, id_suscripcion):
    suscripcion = get_object_or_404(Suscripcion, id_suscripcion=id_suscripcion)
    
    if request.method == 'POST':
        form = SuscripcionForm(request.POST, instance=suscripcion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Suscripción actualizada correctamente')
            return redirect('web:superadmin_suscripcion')
    else:
        form = SuscripcionForm(instance=suscripcion)
    
    contexto = {
        'form': form,
        'suscripcion': suscripcion,
        'rol': 'superadmin',
        'usuario': request.session.get('usuario_id')
    }
    
    return render(request, 'modulos/suscripcion/editar.html', contexto)

@es_superadmin
def superadmin_suscripcion_eliminar(request, id_suscripcion):
    suscripcion = get_object_or_404(Suscripcion, id_suscripcion=id_suscripcion)
    
    if request.method == 'POST':
        suscripcion.delete()
        messages.success(request, 'Suscripción eliminada correctamente')
        return redirect('web:superadmin_suscripcion')
    
    contexto = {
        'suscripcion': suscripcion,
        'rol': 'superadmin',
        'usuario': request.session.get('usuario_id')
    }
    
    return render(request, 'modulos/suscripcion/eliminar.html', contexto)

@es_superadmin
def superadmin_reserva(request):
    # Obtener todas las reservas
    reservas = Reserva.objects.all().order_by('-fecha_creacion')
    
    contexto = {
        'reservas': reservas,
        'rol': 'superadmin',
        'usuario': request.session.get('usuario_id')
    }
    
    return render(request, 'modulos/reserva/index.html', contexto)



@es_superadmin
def superadmin_usuario(request):
    # Get the BARBERO role from the database
    rol_barbero = Rol.objects.get(nombre='Barbero')
    
    # Get all users with BARBERO role through UsuarioRol
    usuarios = UsuarioRol.objects.filter(
        rol=rol_barbero
    ).order_by('usuario__usuario')
    
    contexto = {
        'usuarios': usuarios,
        'rol': 'superadmin',
        'usuario': request.session.get('usuario_id')
    }
    
    return render(request, 'modulos/usuario/index.html', contexto)

@es_superadmin
def superadmin_usuario_crear(request):
    if request.method == 'POST':
        usuario = Usuario.objects.create_user(
            usuario=request.POST['usuario'],
            password=request.POST['password']
        )
        # Get BARBERO role
        rol_barbero = Rol.objects.get(nombre='Barbero')
        # Create UsuarioRol
        UsuarioRol.objects.create(
            usuario=usuario,
            rol=rol_barbero
        )
        messages.success(request, 'Usuario creado exitosamente')
        return redirect('web:superadmin_usuario')
    
    contexto = {
        'rol': 'superadmin',
        'usuario': request.session.get('usuario_id')
    }
    
    return render(request, 'modulos/usuario/crear.html', contexto)

@es_superadmin
def superadmin_usuario_editar(request, id_usuario):
    usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
    
    if request.method == 'POST':
        usuario.usuario = request.POST['usuario']
        if request.POST.get('password', ''):
            usuario.set_password(request.POST['password'])
        usuario.save()
        messages.success(request, 'Usuario actualizado exitosamente')
        return redirect('web:superadmin_usuario')
    
    contexto = {
        'usuario_obj': usuario,
        'rol': 'superadmin',
        'usuario': request.session.get('usuario_id')
    }
    
    return render(request, 'modulos/usuario/editar.html', contexto)

@es_superadmin
def superadmin_usuario_eliminar(request, id_usuario):
    usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
    
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado exitosamente')
        return redirect('web:superadmin_usuario')
    
    contexto = {
        'usuario': usuario,
        'rol': 'superadmin',
        'usuario': request.session.get('usuario_id')
    }
    
    return render(request, 'modulos/usuario/eliminar.html', contexto)

def cancelar_reserva(request):
    if request.method == 'POST':
        reserva_id = request.POST.get('reserva_id')
        if not reserva_id:
            messages.error(request, 'ID de reserva no proporcionado')
            print(f"DEBUG: No se recibió ID de reserva")
            return redirect('web:index')
            
        try:
            reserva = Reserva.objects.get(id_reserva=reserva_id)
            print(f"DEBUG: Reserva encontrada: {reserva.id_reserva}, Cliente: {reserva.cliente.id_cliente}")
            
            # Get client ID from session
            cliente_id = request.session.get('cliente_id')
            print(f"DEBUG: ID de cliente en sesión: {cliente_id}")
            
            if not cliente_id:
                messages.error(request, 'No se pudo obtener el ID del cliente')
                print("DEBUG: No se encontró ID de cliente en sesión")
                return redirect('web:index')
                
            try:
                cliente_id = int(cliente_id)
                print(f"DEBUG: ID de cliente convertido: {cliente_id}")
                
                if reserva.cliente.id_cliente != cliente_id:
                    messages.error(request, 'No tienes permiso para cancelar esta reserva')
                    print(f"DEBUG: IDs no coinciden - Reserva: {reserva.cliente.id_cliente}, Cliente: {cliente_id}")
                    return redirect('web:index')
                    
                if reserva.estado != 'pendiente':
                    messages.error(request, 'Solo se pueden cancelar reservas pendientes')
                    print(f"DEBUG: Estado de la reserva: {reserva.estado}")
                    return redirect('web:index')
                    
                reserva.estado = 'cancelada'
                reserva.save()
                messages.success(request, 'Reserva cancelada exitosamente')
                print(f"DEBUG: Reserva cancelada exitosamente para cliente {cliente_id}")
                return redirect('web:index')
                
            except ValueError:
                messages.error(request, 'ID de cliente inválido en la sesión')
                print(f"DEBUG: Error al convertir ID de cliente: {cliente_id}")
                return redirect('web:index')
            
        except Reserva.DoesNotExist:
            messages.error(request, 'Reserva no encontrada')
            print(f"DEBUG: Reserva no encontrada: {reserva_id}")
            return redirect('web:index')
            
        except ValueError:
            messages.error(request, 'ID de cliente inválido en la sesión')
            return redirect('web:index')
            
    return redirect('web:index')

def check_employee_availability(request):
    if request.method == 'GET':
        empleado_id = request.GET.get('empleado_id')
        fecha = request.GET.get('fecha')
        hora = request.GET.get('hora')
        
        if not all([empleado_id, fecha, hora]):
            return JsonResponse({'error': 'Faltan parámetros requeridos'}, status=400)
            
        try:
            # Verificar si ya existe una reserva para ese empleado, fecha y hora
            existing_reserva = Reserva.objects.filter(
                empleado_id=empleado_id,
                fecha=fecha,
                hora=hora,
                estado__in=['pendiente', 'confirmada']
            ).exists()
            
            if existing_reserva:
                # Si está ocupado, obtener empleados disponibles para esa fecha y hora
                disponibles = Empleado.objects.filter(
                    negocio_id=Reserva.objects.get(id_reserva=existing_reserva).negocio_id
                ).exclude(
                    id_empleado__in=Reserva.objects.filter(
                        fecha=fecha,
                        hora=hora,
                        estado__in=['pendiente', 'confirmada']
                    ).values('empleado_id')
                )
                
                return JsonResponse({
                    'available': False,
                    'message': 'Este empleado ya tiene una cita programada para esa fecha y hora',
                    'available_employees': list(disponibles.values('id_empleado', 'nombre'))
                })
            else:
                return JsonResponse({'available': True})
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@es_superadmin
def crear_empleado(request):
    if request.method == 'POST':
        try:
            usuario_id = request.POST.get('usuario_id')
            negocio_id = request.POST.get('negocio_id')
            
            if not usuario_id or not negocio_id:
                messages.error(request, 'Faltan parámetros requeridos')
                return redirect('web:superadmin_usuario')
            
            # Obtener el usuario y el negocio
            usuario = Usuario.objects.get(id_usuario=usuario_id)
            negocio = Negocio.objects.get(id_negocio=negocio_id)
            
            # Verificar si ya existe un empleado para este usuario
            if Empleado.objects.filter(usuario=usuario).exists():
                messages.warning(request, 'Este usuario ya tiene un empleado registrado')
                return redirect('web:superadmin_usuario')
            
            # Crear el empleado
            empleado = Empleado.objects.create(
                usuario=usuario,
                negocio=negocio,
                nombre=usuario.usuario,  # Usar el nombre de usuario como nombre inicial
                apellido='',  # Campo opcional
                telefono='',  # Campo opcional
                especialidad='Empleado',  # Valor por defecto
                experiencia_anios=0,  # Valor por defecto
                activo=True
            )
            
            # Obtener o crear el rol de empleado
            rol_empleado, creado = Rol.objects.get_or_create(nombre='Empleado')
            
            # Asignar el rol al usuario
            UsuarioRol.objects.create(
                usuario=usuario,
                rol=rol_empleado
            )
            
            messages.success(request, 'Empleado creado exitosamente')
            return redirect('web:superadmin_usuario')
            
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
        except Negocio.DoesNotExist:
            messages.error(request, 'Negocio no encontrado')
        except Exception as e:
            messages.error(request, f'Error al crear el empleado: {str(e)}')
            
    return redirect('web:superadmin_usuario')