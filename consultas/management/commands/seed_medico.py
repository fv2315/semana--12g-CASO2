from datetime import date, time, timedelta

from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand

from consultas.models import Paciente, Medico, Cita


class Command(BaseCommand):
    help = 'Carga usuarios, roles y datos de prueba del Caso 2'

    def handle(self, *args, **options):
        nombres_grupos = ['Admins', 'Medicos', 'Recepcionistas', 'Pacientes']
        for nombre in nombres_grupos:
            Group.objects.get_or_create(name=nombre)

        admins = Group.objects.get(name='Admins')
        medicos = Group.objects.get(name='Medicos')
        recepcionistas = Group.objects.get(name='Recepcionistas')
        pacientes = Group.objects.get(name='Pacientes')

        for codename in ('agendar_cita', 'cancelar_cita', 'ver_historial_clinico', 'generar_reportes'):
            permiso = Permission.objects.filter(codename=codename).first()
            if permiso:
                admins.permissions.add(permiso)

        for codename in ('ver_historial_clinico', 'cancelar_cita'):
            permiso = Permission.objects.filter(codename=codename).first()
            if permiso:
                medicos.permissions.add(permiso)

        for codename in ('agendar_cita', 'cancelar_cita'):
            permiso = Permission.objects.filter(codename=codename).first()
            if permiso:
                recepcionistas.permissions.add(permiso)

        permiso_historial = Permission.objects.filter(codename='ver_historial_clinico').first()
        if permiso_historial:
            pacientes.permissions.add(permiso_historial)

        admin_user, _ = User.objects.get_or_create(username='admin', defaults={'is_superuser': True, 'is_staff': True})
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.set_password('admin123')
        admin_user.save()
        admin_user.groups.add(admins)

        especialidades = ['Medicina General', 'Cardiologia', 'Dermatologia', 'Pediatria',
                          'Ginecologia', 'Neurologia', 'Traumatologia', 'Odontologia']
        objetos_medicos = []
        for i, especialidad in enumerate(especialidades, 1):
            user, _ = User.objects.get_or_create(username=f'medico{i}', defaults={
                'first_name': f'Dr. Nombre{i}', 'last_name': 'UNCP'})
            user.set_password('medico123')
            user.save()
            user.groups.add(medicos)
            medico, _ = Medico.objects.update_or_create(
                usuario=user,
                defaults={'cmp': f'{12340+i}', 'especialidad': especialidad,
                          'horario_inicio': time(8), 'horario_fin': time(18),
                          'consultorio': f'C-{i:02}'},
            )
            objetos_medicos.append(medico)

        objetos_pacientes = []
        for i in range(1, 16):
            user, _ = User.objects.get_or_create(username=f'paciente{i}', defaults={
                'first_name': f'Paciente{i}', 'last_name': 'UNCP'})
            user.set_password('paciente123')
            user.save()
            user.groups.add(pacientes)
            paciente, _ = Paciente.objects.update_or_create(
                usuario=user,
                defaults={'dni': f'{70000000+i}', 'nombres': f'Paciente{i}',
                          'apellidos': 'UNCP', 'fecha_nacimiento': date(1998, 1, (i % 28) + 1),
                          'tipo': 'estudiante', 'codigo_uncp': f'2026{i:04}',
                          'alergias': 'Ninguna' if i % 2 else 'Penicilina',
                          'email': f'paciente{i}@uncp.edu.pe'},
            )
            objetos_pacientes.append(paciente)

        recepcion, _ = User.objects.get_or_create(username='recepcion', defaults={
            'first_name': 'Ana', 'last_name': 'Recepción'})
        recepcion.set_password('recepcion123')
        recepcion.save()
        recepcion.groups.add(recepcionistas)

        base = date.today() + timedelta(days=1)
        for i in range(30):
            medico = objetos_medicos[i % len(objetos_medicos)]
            paciente = objetos_pacientes[i % len(objetos_pacientes)]
            hora = time(8 + (i % 8), 0)
            Cita.objects.get_or_create(
                medico=medico, fecha=base + timedelta(days=i // 8),
                hora=hora,
                defaults={'paciente': paciente, 'motivo': 'Control medico general y evaluacion de sintomas.',
                          'estado': 'pendiente'},
            )

        self.stdout.write(self.style.SUCCESS('Datos de prueba cargados correctamente'))
