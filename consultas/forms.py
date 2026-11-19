import re
from datetime import date, time

from django import forms
from django.utils.html import strip_tags

from .models import Paciente, Medico, Cita, Consulta


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['dni', 'nombres', 'apellidos', 'fecha_nacimiento', 'tipo', 'codigo_uncp', 'alergias', 'email']
        widgets = {'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'})}

    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if not re.fullmatch(r'\d{8}', dni):
            raise forms.ValidationError('El DNI debe contener exactamente 8 dígitos.')
        return dni

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data['fecha_nacimiento']
        if fecha > date.today():
            raise forms.ValidationError('La fecha de nacimiento no puede ser futura.')
        return fecha

    def clean_email(self):
        email = self.cleaned_data['email']
        tipo = self.cleaned_data.get('tipo')
        if tipo == 'estudiante' and not email.lower().endswith('@uncp.edu.pe'):
            raise forms.ValidationError('Los estudiantes deben usar un correo @uncp.edu.pe.')
        return email


class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['cmp', 'especialidad', 'horario_inicio', 'horario_fin', 'consultorio']

    def clean_cmp(self):
        cmp = self.cleaned_data['cmp']
        if not re.fullmatch(r'\d{5}', cmp):
            raise forms.ValidationError('El CMP debe tener exactamente 5 dígitos.')
        return cmp


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['paciente', 'medico', 'fecha', 'hora', 'motivo']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean_motivo(self):
        motivo = strip_tags(self.cleaned_data['motivo']).strip()
        if len(motivo) < 20:
            raise forms.ValidationError('El motivo debe tener al menos 20 caracteres.')
        return motivo

    def clean(self):
        cleaned = super().clean()
        paciente = cleaned.get('paciente')
        medico = cleaned.get('medico')
        fecha = cleaned.get('fecha')
        hora = cleaned.get('hora')
        if fecha and hora and paciente:
            if Cita.objects.filter(paciente=paciente, fecha=fecha).exclude(
                    estado='cancelada').exists():
                raise forms.ValidationError('El paciente ya tiene una cita el mismo día.')
        if fecha and hora and medico:
            if Cita.objects.filter(medico=medico, fecha=fecha, hora=hora).exclude(
                    estado='cancelada').exists():
                raise forms.ValidationError('El médico ya tiene ocupada esa hora.')
            if hora < medico.horario_inicio or hora > medico.horario_fin:
                raise forms.ValidationError('La cita está fuera del horario de atención del médico.')
            if fecha.weekday() == 5 and hora > time(13, 0):
                raise forms.ValidationError('El horario del sábado termina a las 13:00.')
            if fecha < date.today():
                raise forms.ValidationError('La cita no puede estar en una fecha pasada.')
        return cleaned


class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['diagnostico', 'tratamiento', 'medicamentos', 'proxima_cita', 'archivos', 'notas']
        widgets = {'proxima_cita': forms.DateInput(attrs={'type': 'date'})}

    def clean_diagnostico(self):
        return strip_tags(self.cleaned_data['diagnostico']).strip()

    def clean_tratamiento(self):
        return strip_tags(self.cleaned_data['tratamiento']).strip()
