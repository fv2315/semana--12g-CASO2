from datetime import date, time

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .forms import CitaForm, PacienteForm
from .models import Medico, Paciente


class ValidacionCaso2Tests(TestCase):
    def setUp(self):
        grupo_pacientes = Group.objects.create(name='Pacientes')
        grupo_medicos = Group.objects.create(name='Medicos')

        usuario_paciente = User.objects.create_user('paciente_test', password='clave123')
        usuario_paciente.groups.add(grupo_pacientes)
        self.paciente = Paciente.objects.create(
            usuario=usuario_paciente, dni='12345678', nombres='Ana',
            apellidos='Prueba', fecha_nacimiento=date(2000, 1, 1),
            tipo='estudiante', codigo_uncp='20260001', alergias='',
            email='ana@uncp.edu.pe',
        )

        usuario_medico = User.objects.create_user('medico_test', password='clave123')
        usuario_medico.groups.add(grupo_medicos)
        self.medico = Medico.objects.create(
            usuario=usuario_medico, cmp='12345', especialidad='Medicina General',
            horario_inicio=time(8, 0), horario_fin=time(18, 0), consultorio='C-1',
        )

    def test_paciente_dni_invalido(self):
        form = PacienteForm(data={
            'dni': '12A45678', 'nombres': 'Ana', 'apellidos': 'Prueba',
            'fecha_nacimiento': '2000-01-01', 'tipo': 'estudiante',
            'codigo_uncp': '20260001', 'alergias': '', 'email': 'ana@uncp.edu.pe',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('dni', form.errors)

    def test_fecha_nacimiento_futura(self):
        form = PacienteForm(data={
            'dni': '12345679', 'nombres': 'Ana', 'apellidos': 'Prueba',
            'fecha_nacimiento': '2099-01-01', 'tipo': 'docente',
            'codigo_uncp': '20260002', 'alergias': '', 'email': 'ana@gmail.com',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_nacimiento', form.errors)

    def test_cita_fuera_horario(self):
        form = CitaForm(data={
            'paciente': self.paciente.id, 'medico': self.medico.id,
            'fecha': date.today().isoformat(), 'hora': '19:00',
            'motivo': 'Consulta médica para evaluación general.',
        })
        self.assertFalse(form.is_valid())

    def test_login_redirige_a_citas(self):
        response = self.client.post(reverse('login'), {
            'username': 'paciente_test', 'password': 'clave123',
        })
        self.assertEqual(response.status_code, 302)
