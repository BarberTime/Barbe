from apps.usuario_rol.models import UsuarioRol
from django.shortcuts import render, redirect
from apps.usuario.models import Usuario
def index(request):
    usuarios =  Usuario.objects.all()
    return render(request, 'web:dashboard', {'usuarios': usuarios})

def crearUsuario(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        usuario = Usuario.objects.create_user(usuario=nombre, password='password')
        return redirect('usuario:index')
    
    return render(request, 'modulos/usuario/crear_usuario.html')

def listaUsuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'modulos/usuario/lista_usuarios.html', {'usuarios': usuarios})

def actualizarUsuario(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    if request.method == 'POST':
        usuario.usuario = request.POST['nombre']
        usuario.save()
        return redirect('usuario:index')
    
    return render(request, 'modulos/usuario/actualizar_usuario.html', {'usuario': usuario})

def eliminarUsuario(request, id_usuario):
    usuario = Usuario.objects.get(id_usuario=id_usuario)
    usuario.delete()
    return redirect('usuario:index')

def iniciarSesion(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        usuario = Usuario.objects.get(username=nombre)
        if usuario is not None:
            login(request, usuario)
            return redirect('web:dashboard')
    
    return render(request, 'modulos/usuario/iniciar_sesion.html')

def cerrarSesion(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
       
    return redirect('login')
