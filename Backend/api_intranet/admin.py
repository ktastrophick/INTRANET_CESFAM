# api_intranet/admin.py

from django.contrib import admin
from .models import (
    RolUsuario,
    Cargo,
    Departamento,
    Usuario,
    Evento,
    Solicitud,
    EstadoSolicitud,
)

# ----------------------------------------
# ADMIN RolUsuario
# ----------------------------------------
@admin.register(RolUsuario)
class RolUsuarioAdmin(admin.ModelAdmin):
    list_display = ("id_rol", "nombre")
    search_fields = ("nombre",)
    ordering = ("nombre",)


# ----------------------------------------
# ADMIN Cargo
# ----------------------------------------
@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ("id_cargo", "nombre")
    search_fields = ("nombre",)
    ordering = ("nombre",)


# ----------------------------------------
# ADMIN Departamento
# ----------------------------------------
@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ("id_departamento", "nombre")
    search_fields = ("nombre",)
    ordering = ("nombre",)


# ----------------------------------------
# ADMIN Usuario
# ----------------------------------------
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "id_usuario",
        "rut",
        "dv",
        "nombre",
        "correo",
        "telefono",
        "id_rol",
        "id_departamento",
        "id_cargo",
        "fecha_registro",
    )
    list_filter = ("id_rol", "id_departamento", "id_cargo")
    search_fields = ("rut", "nombre", "correo")
    ordering = ("nombre",)

    fieldsets = (
        ("Datos de identificación", {
            "fields": ("rut", "dv", "nombre")
        }),
        ("Contacto", {
            "fields": ("telefono", "correo")
        }),
        ("Información organizacional", {
            "fields": ("id_rol", "id_departamento", "id_cargo")
        }),
        ("Seguridad y registro", {
            "fields": ("contrasena", "fecha_registro")
        }),
    )


# ----------------------------------------
# ADMIN Evento
# ----------------------------------------
@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "fecha", "tipo", "usuario", "color", "fecha_registro")
    list_filter = ("tipo", "usuario", "fecha")
    search_fields = ("titulo", "descripcion")
    ordering = ("-fecha",)
    readonly_fields = ("fecha_registro",)

    fieldsets = (
        ("Información del Evento", {
            "fields": ("titulo", "descripcion", "fecha", "color", "tipo")
        }),
        ("Metadatos", {
            "fields": ("usuario", "fecha_registro"),
            "classes": ("collapse",)
        }),
    )


# ----------------------------------------
# ADMIN EstadoSolicitud
# ----------------------------------------
@admin.register(EstadoSolicitud)
class EstadoSolicitudAdmin(admin.ModelAdmin):
    list_display = ("id_estados", "nombre")
    search_fields = ("nombre",)
    ordering = ("nombre",)

# ----------------------------------------
# ADMIN Solicitud
# ----------------------------------------
@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    """
    Administración básica de solicitudes.

    No asumimos nombres de campos como 'titulo', 'estado', etc.,
    para evitar los errores admin.E108/E116/E033 que ya viste.
    """
    pass
