from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Rol
from apps.web.decorators import es_superadmin

@es_superadmin
def index(request):
    roles = Rol.objects.all()
    return render(request, 'modulos/rol/index.html', {'roles': roles})

@es_superadmin
def crear(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        
        rol = Rol.objects.create(nombre=nombre)
        
        messages.success(request, 'Rol creado exitosamente')
        return redirect('rol:index')
    
    return render(request, 'modulos/rol/crear.html')

@es_superadmin
def editar(request, id_rol):
    rol = get_object_or_404(Rol, id_rol=id_rol)
    
    if request.method == 'POST':
        rol.nombre = request.POST['nombre']
        rol.save()
        
        messages.success(request, 'Rol actualizado exitosamente')
        return redirect('rol:index')
    
    return render(request, 'modulos/rol/editar.html', {'rol': rol})

@es_superadmin
def eliminar(request, id_rol):
    rol = get_object_or_404(Rol, id_rol=id_rol)
    
    if request.method == 'POST':
        rol.delete()
        messages.success(request, 'Rol eliminado exitosamente')
        return redirect('rol:index')
    
    return render(request, 'modulos/rol/eliminar.html', {'rol': rol})
