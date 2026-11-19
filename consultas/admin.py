from django.contrib import admin

from .models import Paciente, Medico, Cita, Consulta, LogMedico


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('dni', 'nombres', 'apellidos', 'tipo', 'edad')
    search_fields = ('dni', 'nombres', 'apellidos')
    list_filter = ('tipo',)


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cmp', 'especialidad', 'consultorio')
    search_fields = ('cmp', 'especialidad', 'usuario__first_name', 'usuario__last_name')
    list_filter = ('especialidad',)


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'medico', 'fecha', 'hora', 'estado')
    list_filter = ('estado', 'fecha', 'medico__especialidad')
    search_fields = ('paciente__dni', 'paciente__nombres', 'medico__especialidad')
    date_hierarchy = 'fecha'
    actions = ['marcar_completadas']

    @admin.action(description='Marcar citas como completadas')
    def marcar_completadas(self, request, queryset):
        queryset.update(estado='completada')


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('cita', 'diagnostico', 'registrada_por', 'registrada_en')
    readonly_fields = ('cita', 'diagnostico', 'tratamiento', 'medicamentos',
                       'proxima_cita', 'archivos', 'registrada_en', 'registrada_por')

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(LogMedico)
class LogMedicoAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'usuario', 'accion', 'ip')
    list_filter = ('accion', 'fecha_hora')
