from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.usuario.models import Usuario
from django.contrib.auth.decorators import login_required
from .models import UsuarioRol
from apps.rol.models import Rol
from apps.web.decorators import es_superadmin

@es_superadmin
def index(request):
    usuarios_roles = UsuarioRol.objects.all().order_by('-fecha_registro')
    return render(request, 'modulos/usuario_rol/index.html', {'usuarios_roles': usuarios_roles})

@es_superadmin
def crear(request):
    if request.method == 'POST':
        usuario_id = request.POST['usuario']
        rol_id = request.POST['rol']
        
        usuario = Usuario.objects.get(id=usuario_id)
        rol = Rol.objects.get(id_rol=rol_id)
        
        # Verificar si ya existe la relación
        if UsuarioRol.objects.filter(usuario=usuario, rol=rol).exists():
            messages.error(request, 'Esta relación usuario-rol ya existe')
            return redirect('usuario_rol:crear')
        
        usuario_rol = UsuarioRol.objects.create(
            usuario=usuario,
            rol=rol
        )
        
        messages.success(request, 'Relación usuario-rol creada exitosamente')
        return redirect('usuario_rol:index')
    
    usuarios = Usuario.objects.all()
    roles = Rol.objects.all()
    
    return render(request, 'modulos/usuario_rol/crear.html', {
        'usuarios': usuarios,
        'roles': roles
    })

@es_superadmin  
def editar(request, id_usuario_rol):
    usuario_rol = get_object_or_404(UsuarioRol, id_usuario_rol=id_usuario_rol)
    
    if request.method == 'POST':
        rol_id = request.POST['rol']
        rol = Rol.objects.get(id_rol=rol_id)
        
        # Verificar si ya existe la relación con el nuevo rol
        if UsuarioRol.objects.filter(usuario=usuario_rol.usuario, rol=rol).exclude(id_usuario_rol=usuario_rol.id_usuario_rol).exists():
            messages.error(request, 'Esta relación usuario-rol ya existe')
            return redirect('usuario_rol:editar', id_usuario_rol=usuario_rol.id_usuario_rol)
        
        usuario_rol.rol = rol
        usuario_rol.save()
        
        messages.success(request, 'Relación usuario-rol actualizada exitosamente')
        return redirect('usuario_rol:index')
    
    roles = Rol.objects.all()
    
    return render(request, 'modulos/usuario_rol/editar.html', {
        'usuario_rol': usuario_rol,
        'roles': roles
    })

@es_superadmin
def eliminar(request, id_usuario_rol):
    usuario_rol = get_object_or_404(UsuarioRol, id_usuario_rol=id_usuario_rol)
    
    if request.method == 'POST':
        usuario_rol.delete()
        messages.success(request, 'Relación usuario-rol eliminada exitosamente')
        return redirect('usuario_rol:index')
    
    return render(request, 'modulos/usuario_rol/eliminar.html', {'usuario_rol': usuario_rol})
