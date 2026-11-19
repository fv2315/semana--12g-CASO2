from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, render, get_object_or_404
from .forms import CitaForm, ConsultaForm
from .models import Cita, Consulta, Medico, Paciente, LogMedico


def salir(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('inicio')


def inicio(request):
    return render(request, 'consultas/inicio.html')


@login_required
def cita_nueva(request):
    if not (request.user.groups.filter(name__in=['Recepcionistas', 'Pacientes', 'Admins']).exists()
            or request.user.has_perm('consultas.agendar_cita')):
        LogMedico.objects.create(usuario=request.user, accion='ACCESO_DENEGADO',
                                 detalle='Intento de agendar cita', ip=request.META.get('REMOTE_ADDR'))
        return render(request, 'consultas/403.html', status=403)

    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            if hasattr(request.user, 'paciente') and not request.user.groups.filter(name='Recepcionistas').exists():
                cita.paciente = request.user.paciente
            cita.save()
            LogMedico.objects.create(usuario=request.user, accion='CITA_CREADA',
                                     detalle=f'Cita {cita.id}', ip=request.META.get('REMOTE_ADDR'))
            messages.success(request, 'Cita agendada correctamente.')
            return redirect('mis_citas')
    else:
        form = CitaForm()
    return render(request, 'consultas/formulario.html', {'form': form, 'titulo': 'Agendar cita médica'})


@login_required
def mis_citas(request):
    if hasattr(request.user, 'paciente'):
        citas = Cita.objects.filter(paciente=request.user.paciente).select_related('medico', 'paciente')
    elif hasattr(request.user, 'medico'):
        citas = Cita.objects.filter(medico=request.user.medico).select_related('medico', 'paciente')
    else:
        citas = Cita.objects.all().select_related('medico', 'paciente')
    return render(request, 'consultas/citas.html', {'citas': citas})


@login_required
def historial(request, paciente_id=None):
    if hasattr(request.user, 'paciente'):
        paciente = request.user.paciente
        if paciente_id and paciente_id != paciente.id:
            return render(request, 'consultas/403.html', status=403)
    elif hasattr(request.user, 'medico'):
        paciente = get_object_or_404(Paciente, pk=paciente_id)
    elif request.user.groups.filter(name='Admins').exists():
        paciente = get_object_or_404(Paciente, pk=paciente_id)
    else:
        return render(request, 'consultas/403.html', status=403)

    consultas = Consulta.objects.filter(cita__paciente=paciente).select_related(
        'cita', 'cita__medico', 'registrada_por')
    LogMedico.objects.create(usuario=request.user, accion='HISTORIAL_ACCEDIDO',
                             detalle=f'Paciente {paciente.id}', ip=request.META.get('REMOTE_ADDR'))
    return render(request, 'consultas/historial.html', {'paciente': paciente, 'consultas': consultas})


@login_required
def consulta_nueva(request, cita_id):
    cita = get_object_or_404(Cita.objects.select_related('paciente', 'medico'), pk=cita_id)
    if not hasattr(request.user, 'medico') or cita.medico != request.user.medico:
        return render(request, 'consultas/403.html', status=403)
    if hasattr(cita, 'consulta'):
        messages.error(request, 'La consulta ya fue registrada y no puede modificarse.')
        return redirect('mis_citas')
    form = ConsultaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        consulta = form.save(commit=False)
        consulta.cita = cita
        consulta.registrada_por = request.user
        consulta.save()
        cita.estado = 'completada'
        cita.save(update_fields=['estado'])
        LogMedico.objects.create(usuario=request.user, accion='CONSULTA_REGISTRADA',
                                 detalle=f'Consulta cita {cita.id}', ip=request.META.get('REMOTE_ADDR'))
        messages.success(request, 'Consulta registrada.')
        return redirect('mis_citas')
    return render(request, 'consultas/formulario.html', {'form': form, 'titulo': 'Registrar consulta médica'})


@login_required
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    permitido = hasattr(request.user, 'medico') or hasattr(request.user, 'paciente') and cita.paciente == request.user.paciente
    permitido = permitido or request.user.groups.filter(name='Recepcionistas').exists()
    if not permitido:
        return render(request, 'consultas/403.html', status=403)
    cita.estado = 'cancelada'
    cita.save(update_fields=['estado'])
    LogMedico.objects.create(usuario=request.user, accion='CITA_CANCELADA',
                             detalle=f'Cita {cita.id}', ip=request.META.get('REMOTE_ADDR'))
    messages.success(request, 'Cita cancelada.')
    return redirect('mis_citas')
