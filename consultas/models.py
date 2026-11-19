from datetime import date

from django.contrib.auth.models import User
from django.db import models


class Paciente(models.Model):
    TIPO_CHOICES = [('estudiante', 'Estudiante'), ('docente', 'Docente')]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    dni = models.CharField(max_length=8, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    tipo = models.CharField(max_length=12, choices=TIPO_CHOICES)
    codigo_uncp = models.CharField(max_length=20)
    alergias = models.TextField(blank=True)
    email = models.EmailField()

    def edad(self):
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class Medico(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cmp = models.CharField(max_length=5, unique=True)
    especialidad = models.CharField(max_length=100)
    horario_inicio = models.TimeField(default='08:00')
    horario_fin = models.TimeField(default='18:00')
    consultorio = models.CharField(max_length=30)

    def __str__(self):
        return f"Dr(a). {self.usuario.get_full_name()} - {self.especialidad}"


class Cita(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('no_asistio', 'No asistió'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='citas')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField()
    estado = models.CharField(max_length=12, choices=ESTADOS, default='pendiente')
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['fecha', 'hora']
        permissions = [('cancelar_cita', 'Puede cancelar citas'), ('agendar_cita', 'Puede agendar citas')]
        unique_together = ('medico', 'fecha', 'hora')

    def __str__(self):
        return f"{self.paciente} - {self.medico.especialidad} ({self.fecha} {self.hora})"


class Consulta(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.PROTECT, related_name='consulta')
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    medicamentos = models.TextField(blank=True)
    proxima_cita = models.DateField(null=True, blank=True)
    archivos = models.TextField(blank=True)
    notas = models.TextField(blank=True)
    registrada_en = models.DateTimeField(auto_now_add=True)
    registrada_por = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        permissions = [('ver_historial_clinico', 'Puede ver historiales clínicos')]

    def __str__(self):
        return f"Consulta de {self.cita.paciente}"


class LogMedico(models.Model):
    usuario = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    accion = models.CharField(max_length=100)
    detalle = models.TextField(blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fecha_hora}: {self.accion}"
