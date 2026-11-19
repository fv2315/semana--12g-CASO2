import logging
from datetime import date, datetime, time

from django.contrib import messages
from django.shortcuts import render

from .models import Cita, LogMedico

logger = logging.getLogger('centro_medico')


class MedicalAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and '/historial/' in request.path:
            logger.info(
                'ACCESO_SENSIBLE usuario=%s ip=%s ruta=%s',
                request.user.username,
                request.META.get('REMOTE_ADDR'),
                request.path,
            )
        return response


class AppointmentScheduleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            medico = getattr(request.user, 'medico', None)
            if medico and not getattr(request, '_alerta_medico', False):
                pendientes = Cita.objects.filter(medico=medico, estado='pendiente').count()
                if pendientes:
                    messages.warning(request, f'Tiene {pendientes} cita(s) médica(s) pendiente(s).')
                request._alerta_medico = True

            if request.method == 'POST' and request.path.endswith('/citas/nueva/'):
                fuera_horario = False
                detalle = 'Intento de agendamiento fuera de horario'
                try:
                    fecha = date.fromisoformat(request.POST.get('fecha', ''))
                    hora = datetime.strptime(request.POST.get('hora', ''), '%H:%M').time()
                    if fecha.weekday() > 5:
                        fuera_horario = True
                        detalle = 'Intento de cita fuera del calendario de atención'
                    elif fecha.weekday() == 5 and hora > time(13, 0):
                        fuera_horario = True
                        detalle = 'Intento de cita fuera del horario del sábado'
                    elif hora < time(8, 0) or hora > time(18, 0):
                        fuera_horario = True
                        detalle = 'Intento de cita fuera del horario de atención'
                except (TypeError, ValueError):
                    fuera_horario = False

                if fuera_horario:
                    LogMedico.objects.create(
                        usuario=request.user,
                        accion='VALIDACION_HORARIO',
                        detalle=detalle,
                        ip=request.META.get('REMOTE_ADDR'),
                    )
                    logger.warning('%s usuario=%s ip=%s', detalle, request.user.username,
                                   request.META.get('REMOTE_ADDR'))
                    return render(request, 'consultas/403.html',
                                  {'mensaje': detalle}, status=403)
        return self.get_response(request)
