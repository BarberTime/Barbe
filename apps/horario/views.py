from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Horario
from apps.negocio.models import Negocio
from apps.usuario.models import Usuario
from apps.web.decorators import es_barbero_o_superadmin

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
            horarios = Horario.objects.filter(negocio=negocio).order_by('dia', 'hora_inicio')
            return render(request, 'modulos/horario/index.html', {
                'horarios': horarios,
                'usuario': usuario,
                'negocio': negocio
            })
        except Negocio.DoesNotExist:
            messages.warning(request, 'No tienes un negocio registrado')
            return render(request, 'modulos/horario/index.html', {
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
                dia = request.POST['dia']
                hora_inicio = request.POST['hora_inicio']
                hora_fin = request.POST['hora_fin']
                
                # Validar que la hora de fin sea mayor que la de inicio
                if hora_inicio >= hora_fin:
                    messages.error(request, 'La hora de fin debe ser mayor que la hora de inicio')
                else:
                    # Validar que no exista un horario duplicado para el mismo día
                    if Horario.objects.filter(negocio=negocio, dia=dia, hora_inicio=hora_inicio, hora_fin=hora_fin).exists():
                        messages.error(request, 'Ya existe un horario igual para este día')
                    else:
                        horario = Horario.objects.create(
                            negocio=negocio,
                            dia=dia,
                            hora_inicio=hora_inicio,
                            hora_fin=hora_fin
                        )
                        messages.success(request, 'Horario creado exitosamente')
                        return redirect('horario:index')
                        
            except Negocio.DoesNotExist:
                messages.error(request, 'No tienes un negocio registrado')
            except Exception as e:
                messages.error(request, f'Error al crear el horario: {str(e)}')
        
        # GET - Mostrar formulario
        try:
            negocio = Negocio.objects.get(usuario=usuario)
            dias_semana = [
                ('lunes', 'Lunes'),
                ('martes', 'Martes'),
                ('miercoles', 'Miércoles'),
                ('jueves', 'Jueves'),
                ('viernes', 'Viernes'),
                ('sabado', 'Sábado'),
                ('domingo', 'Domingo'),
            ]
            
            return render(request, 'modulos/horario/crear.html', {
                'negocio': negocio,
                'usuario': usuario,
                'dias_semana': dias_semana
            })
        except Negocio.DoesNotExist:
            messages.warning(request, 'No tienes un negocio registrado')
            return redirect('horario:index')
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no autenticado')
        return redirect('web:login')

@es_barbero_o_superadmin
def editar(request, id_horario):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, 'Usuario no autenticado')
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        horario = get_object_or_404(Horario, id_horario=id_horario)
        
        # Verificar permisos
        try:
            negocio = Negocio.objects.get(usuario=usuario)
            if horario.negocio != negocio:
                messages.error(request, 'No tienes permisos para editar este horario')
                return redirect('horario:index')
        except Negocio.DoesNotExist:
            messages.error(request, 'No tienes un negocio registrado')
            return redirect('horario:index')
        
        if request.method == 'POST':
            try:
                dia = request.POST['dia']
                hora_inicio = request.POST['hora_inicio']
                hora_fin = request.POST['hora_fin']
                
                # Validar que la hora de fin sea mayor que la de inicio
                if hora_inicio >= hora_fin:
                    messages.error(request, 'La hora de fin debe ser mayor que la hora de inicio')
                else:
                    # Validar que no exista otro horario duplicado
                    if Horario.objects.filter(negocio=negocio, dia=dia, hora_inicio=hora_inicio, hora_fin=hora_fin).exclude(id_horario=id_horario).exists():
                        messages.error(request, 'Ya existe un horario igual para este día')
                    else:
                        horario.dia = dia
                        horario.hora_inicio = hora_inicio
                        horario.hora_fin = hora_fin
                        horario.save()
                        messages.success(request, 'Horario actualizado exitosamente')
                        return redirect('horario:index')
                        
            except Exception as e:
                messages.error(request, f'Error al actualizar el horario: {str(e)}')
        
        dias_semana = [
            ('lunes', 'Lunes'),
            ('martes', 'Martes'),
            ('miercoles', 'Miércoles'),
            ('jueves', 'Jueves'),
            ('viernes', 'Viernes'),
            ('sabado', 'Sábado'),
            ('domingo', 'Domingo'),
        ]
        
        return render(request, 'modulos/horario/editar.html', {
            'horario': horario,
            'negocio': negocio,
            'usuario': usuario,
            'dias_semana': dias_semana
        })
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no autenticado')
        return redirect('web:login')

@es_barbero_o_superadmin
def eliminar(request, id_horario):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, 'Usuario no autenticado')
        return redirect('web:login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        horario = get_object_or_404(Horario, id_horario=id_horario)
        
        # Verificar permisos
        try:
            negocio = Negocio.objects.get(usuario=usuario)
            if horario.negocio != negocio:
                messages.error(request, 'No tienes permisos para eliminar este horario')
                return redirect('horario:index')
        except Negocio.DoesNotExist:
            messages.error(request, 'No tienes un negocio registrado')
            return redirect('horario:index')
        
        if request.method == 'POST':
            try:
                horario.delete()
                messages.success(request, 'Horario eliminado exitosamente')
                return redirect('horario:index')
            except Exception as e:
                messages.error(request, f'Error al eliminar el horario: {str(e)}')
                return redirect('horario:index')
        
        return render(request, 'modulos/horario/eliminar.html', {
            'horario': horario,
            'negocio': negocio,
            'usuario': usuario
        })
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no autenticado')
        return redirect('web:login')
