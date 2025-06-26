from .models import ImagenesNegocio
from django.shortcuts import render, redirect

def index(request):
    imagenes = ImagenesNegocio.objects.all()
    return render(request, 'modulos/imagenes_negocio/index.html', {'imagenes': imagenes})

def crearImagenesNegocio(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        telefono = request.POST['telefono']
        direccion = request.POST['direccion']
        rol = request.POST['rol']
        negocio = request.POST['negocio']
        empleado = Empleado.objects.create(nombre=nombre, apellido=apellido, telefono=telefono, direccion=direccion, rol=rol, negocio=negocio)
        return redirect('empleado:lista_empleados')
    
    return render(request, 'modulos/imagenes_negocio/crear_empleado.html')

def listaImagenesNegocio(request):
    imagenes = ImagenesNegocio.objects.all()
    return render(request, 'modulos/imagenes_negocio/lista_imagenes_negocio.html', {'imagenes': imagenes})

def actualizarImagenesNegocio(request, id_imagen):
    imagen = ImagenesNegocio.objects.get(id_imagen=id_imagen)
    if request.method == 'POST':
        imagen.nombre = request.POST['nombre']
        imagen.apellido = request.POST['apellido']
        imagen.telefono = request.POST['telefono']
        imagen.direccion = request.POST['direccion']
        imagen.rol = request.POST['rol']
        imagen.negocio = request.POST['negocio']
        imagen.save()
        return redirect('empleado:lista_empleados')
    
    return render(request, 'modulos/imagenes_negocio/actualizar_empleado.html', {'empleado': empleado})

def eliminarImagenesNegocio(request, id_imagen):
    imagen = ImagenesNegocio.objects.get(id_imagen=id_imagen)
    imagen.delete()
    return redirect('empleado:lista_empleados')

