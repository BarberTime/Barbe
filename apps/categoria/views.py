from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Categoria
from apps.web.decorators import es_barbero_o_superadmin, es_empleado
from apps.negocio.models import Negocio
from apps.usuario.models import Usuario

@es_barbero_o_superadmin
def index(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        
        # Get the business associated with this user
        try:
            negocio = Negocio.objects.get(usuario=usuario)
            categorias = Categoria.objects.filter(negocio=negocio).order_by('-fecha_registro')
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
                negocio = Negocio.objects.get(usuario=usuario)
                nombre = request.POST['nombre']
                
                # Validar que no exista una categoría con el mismo nombre
                if Categoria.objects.filter(negocio=negocio, nombre=nombre).exists():
                    messages.error(request, 'Ya existe una categoría con ese nombre')
                else:
                    categoria = Categoria.objects.create(nombre=nombre, negocio=negocio)
                    messages.success(request, 'Categoría creada exitosamente')
                    return redirect('categoria:index')
                    
            except Negocio.DoesNotExist:
                messages.error(request, 'No tienes un negocio registrado')
            except Exception as e:
                messages.error(request, f'Error al crear la categoría: {str(e)}')
        
        # GET - Mostrar formulario
        try:
            negocio = Negocio.objects.get(usuario=usuario)
            return render(request, 'modulos/categoria/crear.html', {
                'negocio': negocio,
                'usuario': usuario
            })
        except Negocio.DoesNotExist:
            messages.warning(request, 'No tienes un negocio registrado')
            return redirect('categoria:index')
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no autenticado')
        return redirect('web:login')

@es_barbero_o_superadmin
def editar(request, id_categoria):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, 'Usuario no autenticado')
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        categoria = get_object_or_404(Categoria, id_categoria=id_categoria)
        
        # Verificar permisos
        try:
            negocio = Negocio.objects.get(usuario=usuario)
            if categoria.negocio != negocio:
                messages.error(request, 'No tienes permisos para editar esta categoría')
                return redirect('categoria:index')
        except Negocio.DoesNotExist:
            messages.error(request, 'No tienes un negocio registrado')
            return redirect('categoria:index')
        
        if request.method == 'POST':
            try:
                nombre = request.POST['nombre']
                
                # Validar que no exista otra categoría con el mismo nombre
                if Categoria.objects.filter(negocio=negocio, nombre=nombre).exclude(id_categoria=id_categoria).exists():
                    messages.error(request, 'Ya existe una categoría con ese nombre')
                else:
                    categoria.nombre = nombre
                    categoria.save()
                    messages.success(request, 'Categoría actualizada exitosamente')
                    return redirect('categoria:index')
                    
            except Exception as e:
                messages.error(request, f'Error al actualizar la categoría: {str(e)}')
        
        return render(request, 'modulos/categoria/editar.html', {
            'categoria': categoria,
            'negocio': negocio,
            'usuario': usuario
        })
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no autenticado')
        return redirect('web:login')

@es_barbero_o_superadmin
def eliminar(request, id_categoria):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, 'Usuario no autenticado')
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        categoria = get_object_or_404(Categoria, id_categoria=id_categoria)
        
        # Verificar permisos
        try:
            negocio = Negocio.objects.get(usuario=usuario)
            if categoria.negocio != negocio:
                messages.error(request, 'No tienes permisos para eliminar esta categoría')
                return redirect('categoria:index')
        except Negocio.DoesNotExist:
            messages.error(request, 'No tienes un negocio registrado')
            return redirect('categoria:index')
        
        if request.method == 'POST':
            try:
                categoria.delete()
                messages.success(request, 'Categoría eliminada exitosamente')
                return redirect('categoria:index')
            except Exception as e:
                messages.error(request, f'Error al eliminar la categoría: {str(e)}')
                return redirect('categoria:index')
        
        return render(request, 'modulos/categoria/eliminar.html', {
            'categoria': categoria,
            'negocio': negocio,
            'usuario': usuario
        })
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no autenticado')
        return redirect('web:login')

@es_empleado
def lista_empleado(request):
    try:
        empleado = request.usuario.empleado
        negocio = empleado.negocio
        categorias = Categoria.objects.filter(negocio=negocio).order_by('nombre')
        return render(request, 'modulos/categoria/lista_empleado.html', {
            'categorias': categorias,
            'negocio': negocio
        })
    except Exception as e:
        messages.error(request, str(e))
        return redirect('web:dashboard_empleado')
