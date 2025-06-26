from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.usuario.decorators import es_barbero_o_superadmin, es_empleado
from .models import Servicio
from apps.categoria.models import Categoria
from apps.negocio.models import Negocio
from apps.usuario.models import Usuario
from apps.empleado.models import Empleado

# Vistas para Categoría
@es_barbero_o_superadmin
def categoria_index(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        try:
            negocio = Negocio.objects.get(usuario=usuario)
            categorias = Categoria.objects.filter(negocio=negocio).order_by('nombre')
            return render(request, 'modulos/categoria/index.html', {
                'categorias': categorias,
                'usuario': usuario,
                'negocio': negocio
            })
        except Negocio.DoesNotExist:
            messages.warning(request, 'No tienes un negocio registrado')
            return render(request, 'modulos/categoria/index.html', {
                'usuario': usuario
            })
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('web:login')

@es_barbero_o_superadmin
def categoria_crear(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        try:
            negocio = Negocio.objects.get(usuario=usuario)
        except Negocio.DoesNotExist:
            messages.warning(request, 'No tienes un negocio registrado')
            return redirect('servicio:categoria_index')
        
        if request.method == 'POST':
            nombre = request.POST.get('nombre', '').strip()
            
            if not nombre:
                messages.error(request, 'El nombre de la categoría es requerido')
                return render(request, 'modulos/categoria/crear.html', {
                    'negocio': negocio
                })
            
            # Verificar si ya existe
            if Categoria.objects.filter(negocio=negocio, nombre__iexact=nombre).exists():
                messages.error(request, 'Ya existe una categoría con ese nombre')
                return render(request, 'modulos/categoria/crear.html', {
                    'negocio': negocio,
                    'nombre': nombre
                })
            
            try:
                categoria = Categoria.objects.create(
                    nombre=nombre,
                    negocio=negocio
                )
                messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente')
                return redirect('servicio:categoria_index')
            except Exception as e:
                messages.error(request, f'Error al crear la categoría: {str(e)}')
        
        return render(request, 'modulos/categoria/crear.html', {
            'negocio': negocio
        })
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('web:login')

@es_barbero_o_superadmin    
def categoria_editar(request, id_categoria):
    categoria = get_object_or_404(Categoria, id_categoria=id_categoria)
    
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        negocio = Negocio.objects.get(usuario=usuario)
        
        # Verificar permisos
        if negocio != categoria.negocio:
            messages.error(request, 'No tienes permisos para editar esta categoría')
            return redirect('servicio:categoria_index')
        
        if request.method == 'POST':
            nombre = request.POST.get('nombre', '').strip()
            
            if not nombre:
                messages.error(request, 'El nombre de la categoría es requerido')
                return render(request, 'modulos/categoria/editar.html', {
                    'categoria': categoria
                })
            
            # Verificar si ya existe otra categoría con ese nombre
            if Categoria.objects.filter(negocio=negocio, nombre__iexact=nombre).exclude(id_categoria=categoria.id_categoria).exists():
                messages.error(request, 'Ya existe una categoría con ese nombre')
                return render(request, 'modulos/categoria/editar.html', {
                    'categoria': categoria,
                    'nombre': nombre
                })
            
            try:
                categoria.nombre = nombre
                categoria.save()
                messages.success(request, f'Categoría "{categoria.nombre}" actualizada exitosamente')
                return redirect('servicio:categoria_index')
            except Exception as e:
                messages.error(request, f'Error al actualizar la categoría: {str(e)}')
        
        return render(request, 'modulos/categoria/editar.html', {
            'categoria': categoria
        })
        
    except (Usuario.DoesNotExist, Negocio.DoesNotExist):
        messages.error(request, 'Error de acceso')
        return redirect('web:login')

@es_barbero_o_superadmin
def categoria_eliminar(request, id_categoria):
    categoria = get_object_or_404(Categoria, id_categoria=id_categoria)
    
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        negocio = Negocio.objects.get(usuario=usuario)
        
        # Verificar permisos
        if negocio != categoria.negocio:
            messages.error(request, 'No tienes permisos para eliminar esta categoría')
            return redirect('servicio:categoria_index')
        
        # Verificar si tiene servicios asociados
        servicios_count = Servicio.objects.filter(categoria=categoria).count()
        
        if request.method == 'POST':
            if servicios_count > 0:
                messages.error(request, f'No se puede eliminar la categoría porque tiene {servicios_count} servicio(s) asociado(s)')
                return redirect('servicio:categoria_index')
            
            try:
                nombre_categoria = categoria.nombre
                categoria.delete()
                messages.success(request, f'Categoría "{nombre_categoria}" eliminada exitosamente')
                return redirect('servicio:categoria_index')
            except Exception as e:
                messages.error(request, f'Error al eliminar la categoría: {str(e)}')
                return redirect('servicio:categoria_index')
        
        return render(request, 'modulos/categoria/eliminar.html', {
            'categoria': categoria,
            'servicios_count': servicios_count
        })
        
    except (Usuario.DoesNotExist, Negocio.DoesNotExist):
        messages.error(request, 'Error de acceso')
        return redirect('web:login')

# Vistas para Servicio
@es_barbero_o_superadmin    
def index(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        try:
            negocio = Negocio.objects.get(usuario=usuario)
            servicios = Servicio.objects.filter(negocio=negocio).select_related('categoria').order_by('-fecha_registro')
            return render(request, 'modulos/servicio/index.html', {
                'servicios': servicios,
                'usuario': usuario,
                'negocio': negocio
            })
        except Negocio.DoesNotExist:
            messages.warning(request, 'No tienes un negocio registrado')
            return render(request, 'modulos/servicio/index.html', {
                'usuario': usuario
            })
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('web:login')

@es_barbero_o_superadmin
def crear(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        try:
            negocio = Negocio.objects.get(usuario=usuario)
        except Negocio.DoesNotExist:
            messages.warning(request, 'No tienes un negocio registrado')
            return redirect('servicio:index')
        
        # Verificar que tenga categorías
        categorias = Categoria.objects.filter(negocio=negocio).order_by('nombre')
        if not categorias.exists():
            messages.warning(request, 'Debes crear al menos una categoría antes de agregar servicios')
            return redirect('servicio:categoria_crear')
        
        if request.method == 'POST':
            # Obtener datos del formulario
            nombre = request.POST.get('nombre', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            precio = request.POST.get('precio', '').strip()
            duracion = request.POST.get('duracion', '').strip()
            categoria_id = request.POST.get('categoria', '').strip()
            
            # Validaciones
            errores = []
            
            if not nombre:
                errores.append('El nombre del servicio es requerido')
            
            if not precio:
                errores.append('El precio es requerido')
            else:
                try:
                    precio_float = float(precio)
                    if precio_float < 0:
                        errores.append('El precio no puede ser negativo')
                except ValueError:
                    errores.append('El precio debe ser un número válido')
            
            if not duracion:
                errores.append('La duración es requerida')
            else:
                try:
                    duracion_int = int(duracion)
                    if duracion_int <= 0:
                        errores.append('La duración debe ser mayor a 0')
                except ValueError:
                    errores.append('La duración debe ser un número entero válido')
            
            if not categoria_id:
                errores.append('Debes seleccionar una categoría')
            else:
                try:
                    categoria = Categoria.objects.get(id_categoria=categoria_id, negocio=negocio)
                except Categoria.DoesNotExist:
                    errores.append('La categoría seleccionada no es válida')
            
            # Verificar si ya existe un servicio con ese nombre
            if nombre and Servicio.objects.filter(negocio=negocio, nombre__iexact=nombre).exists():
                errores.append('Ya existe un servicio con ese nombre')
            
            if errores:
                for error in errores:
                    messages.error(request, error)
                
                return render(request, 'modulos/servicio/crear.html', {
                    'categorias': categorias,
                    'negocio': negocio,
                    'form_data': {
                        'nombre': nombre,
                        'descripcion': descripcion,
                        'precio': precio,
                        'duracion': duracion,
                        'categoria': categoria_id
                    }
                })
            
            try:
                # Crear el servicio
                servicio = Servicio.objects.create(
                    negocio=negocio,
                    nombre=nombre,
                    categoria=categoria,
                    precio=precio_float,
                    descripcion=descripcion,
                    duracion=duracion_int
                )
                
                # Manejar imagen si existe
                if 'imagen' in request.FILES:
                    servicio.imagen = request.FILES['imagen']
                    servicio.save()
                
                messages.success(request, f'Servicio "{servicio.nombre}" creado exitosamente')
                return redirect('servicio:index')
                
            except Exception as e:
                messages.error(request, f'Error al crear el servicio: {str(e)}')
        
        return render(request, 'modulos/servicio/crear.html', {
            'categorias': categorias,
            'negocio': negocio
        })
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('web:login')

@es_barbero_o_superadmin    
def editar(request, id_servicio):
    servicio = get_object_or_404(Servicio, id_servicio=id_servicio)
    
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        negocio = Negocio.objects.get(usuario=usuario)
        
        # Verificar permisos
        if negocio != servicio.negocio:
            messages.error(request, 'No tienes permisos para editar este servicio')
            return redirect('servicio:index')
        
        categorias = Categoria.objects.filter(negocio=negocio).order_by('nombre')
        
        if request.method == 'POST':
            # Obtener datos del formulario
            nombre = request.POST.get('nombre', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            precio = request.POST.get('precio', '').strip()
            duracion = request.POST.get('duracion', '').strip()
            categoria_id = request.POST.get('categoria', '').strip()
            
            # Validaciones
            errores = []
            
            if not nombre:
                errores.append('El nombre del servicio es requerido')
            
            if not precio:
                errores.append('El precio es requerido')
            else:
                try:
                    precio_float = float(precio)
                    if precio_float < 0:
                        errores.append('El precio no puede ser negativo')
                except ValueError:
                    errores.append('El precio debe ser un número válido')
            
            if not duracion:
                errores.append('La duración es requerida')
            else:
                try:
                    duracion_int = int(duracion)
                    if duracion_int <= 0:
                        errores.append('La duración debe ser mayor a 0')
                except ValueError:
                    errores.append('La duración debe ser un número entero válido')
            
            if not categoria_id:
                errores.append('Debes seleccionar una categoría')
            else:
                try:
                    categoria = Categoria.objects.get(id_categoria=categoria_id, negocio=negocio)
                except Categoria.DoesNotExist:
                    errores.append('La categoría seleccionada no es válida')
            
            # Verificar si ya existe otro servicio con ese nombre
            if nombre and Servicio.objects.filter(negocio=negocio, nombre__iexact=nombre).exclude(id_servicio=servicio.id_servicio).exists():
                errores.append('Ya existe un servicio con ese nombre')
            
            if errores:
                for error in errores:
                    messages.error(request, error)
                
                return render(request, 'modulos/servicio/editar.html', {
                    'servicio': servicio,
                    'categorias': categorias,
                    'form_data': {
                        'nombre': nombre,
                        'descripcion': descripcion,
                        'precio': precio,
                        'duracion': duracion,
                        'categoria': categoria_id
                    }
                })
            
            try:
                # Actualizar el servicio
                servicio.nombre = nombre
                servicio.descripcion = descripcion
                servicio.precio = precio_float
                servicio.duracion = duracion_int
                servicio.categoria = categoria
                
                # Manejar imagen si existe
                if 'imagen' in request.FILES:
                    servicio.imagen = request.FILES['imagen']
                
                servicio.save()
                
                messages.success(request, f'Servicio "{servicio.nombre}" actualizado exitosamente')
                return redirect('servicio:index')
                
            except Exception as e:
                messages.error(request, f'Error al actualizar el servicio: {str(e)}')
        
        return render(request, 'modulos/servicio/editar.html', {
            'servicio': servicio,
            'categorias': categorias
        })
        
    except (Usuario.DoesNotExist, Negocio.DoesNotExist):
        messages.error(request, 'Error de acceso')
        return redirect('web:login')

@es_barbero_o_superadmin
def eliminar(request, id_servicio):
    servicio = get_object_or_404(Servicio, id_servicio=id_servicio)
    
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        negocio = Negocio.objects.get(usuario=usuario)
        
        # Verificar permisos
        if negocio != servicio.negocio:
            messages.error(request, 'No tienes permisos para eliminar este servicio')
            return redirect('servicio:index')
        
        if request.method == 'POST':
            try:
                nombre_servicio = servicio.nombre
                servicio.delete()
                messages.success(request, f'Servicio "{nombre_servicio}" eliminado exitosamente')
                return redirect('servicio:index')
            except Exception as e:
                messages.error(request, f'Error al eliminar el servicio: {str(e)}')
                return redirect('servicio:index')
        
        return render(request, 'modulos/servicio/eliminar.html', {
            'servicio': servicio
        })
        
    except (Usuario.DoesNotExist, Negocio.DoesNotExist):
        messages.error(request, 'Error de acceso')
        return redirect('web:login')

@es_empleado
def lista_empleado(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        empleado = Empleado.objects.get(usuario=usuario)
        servicios = Servicio.objects.filter(
            negocio=empleado.negocio, 
            estado='activo'
        ).select_related('categoria').order_by('nombre')
        
        return render(request, 'modulos/servicio/lista_empleado.html', {
            'servicios': servicios,
            'empleado': empleado
        })
    except (Usuario.DoesNotExist, Empleado.DoesNotExist):
        messages.error(request, 'No se pudo acceder a los servicios')
        return redirect('web:dashboard_empleado')
