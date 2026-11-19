# Plataforma de Gestión de Consultas Médicas - Caso 2

Sistema Django para el Centro Médico Universitario de la UNCP.

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_medico
python manage.py runserver
```

## Accesos de prueba

- Administrador: `admin / admin123`
- Médicos: `medico1` a `medico8`, contraseña `medico123`
- Recepción: `recepcion / recepcion123`
- Pacientes: `paciente1` a `paciente15`, contraseña `paciente123`

## Funcionalidades

- Modelos de paciente, médico, cita, consulta clínica y auditoría.
- Validaciones avanzadas de DNI, CMP, correo, fecha, duplicidad y horarios.
- Autenticación, grupos y permisos.
- Middleware de auditoría médica, alertas y sesión de 20 minutos.
- Django Admin con búsquedas, filtros, agenda y acciones masivas.
- Historial clínico protegido y consultas no modificables.

## Diagrama de roles y permisos

```text
Admin
  ├── Gestión total
  ├── ver_historial_clinico
  └── generar_reportes

Médico
  ├── Agenda propia
  ├── ver_historial_clinico
  ├── cancelar_cita
  └── registrar consulta

Recepcionista
  ├── agendar_cita
  ├── cancelar_cita
  └── registrar pacientes

Paciente
  ├── Agendar su cita
  ├── Cancelar su cita
  └── Ver su propio historial
```
