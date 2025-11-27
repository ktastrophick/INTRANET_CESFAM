# api_intranet/admin.py

from django.contrib import admin
from .models import (
    RolUsuario,
    Cargo,
    Departamento,
    Usuario,
    EstadoSolicitud,
    TipoSolicitud,
    Solicitud,
    Calendario,
    TipoCalendario,
    Avisos,
    Licencia,
    Perfil,
    Documento,
    InicioRegistrado,
    Mensajes
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
    list_display = ("id_departamento", "nombre", "jefe_departamento")
    search_fields = ("nombre",)
    list_filter = ("jefe_departamento",)
    ordering = ("nombre",)


# ----------------------------------------
# ADMIN Usuario
# ----------------------------------------
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "id_usuario",
        "rut_completo",
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
    readonly_fields = ("fecha_registro",)

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
# ADMIN EstadoSolicitud
# ----------------------------------------
@admin.register(EstadoSolicitud)
class EstadoSolicitudAdmin(admin.ModelAdmin):
    list_display = ("id_estados", "nombre")
    search_fields = ("nombre",)
    ordering = ("nombre",)


# ----------------------------------------
# ADMIN TipoSolicitud
# ----------------------------------------
@admin.register(TipoSolicitud)
class TipoSolicitudAdmin(admin.ModelAdmin):
    list_display = ("id_tipo", "nombre")
    search_fields = ("nombre",)
    ordering = ("nombre",)


# ----------------------------------------
# ADMIN Solicitud
# ----------------------------------------
@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = (
        "id_solicitud",
        "id_usuario",
        "tipo_solicitud",
        "estado_solicitud",
        "dia_inicio",
        "dia_fin",
        "fecha_registro",
        "aprobacion_jefe",
        "aprobacion_director"
    )
    list_filter = ("tipo_solicitud", "estado_solicitud", "aprobacion_jefe", "aprobacion_director")
    search_fields = ("id_usuario__nombre", "tipo_solicitud__nombre")
    readonly_fields = ("fecha_registro",)
    ordering = ("-fecha_registro",)

    fieldsets = (
        ("Información de la Solicitud", {
            "fields": ("id_usuario", "tipo_solicitud", "estado_solicitud")
        }),
        ("Fechas", {
            "fields": ("dia_inicio", "dia_fin")
        }),
        ("Aprobaciones", {
            "fields": ("aprobacion_jefe", "aprobacion_director"),
            "classes": ("collapse",)
        }),
        ("Registro", {
            "fields": ("fecha_registro",),
            "classes": ("collapse",)
        }),
    )


# ----------------------------------------
# ADMIN TipoCalendario
# ----------------------------------------
@admin.register(TipoCalendario)
class TipoCalendarioAdmin(admin.ModelAdmin):
    list_display = ("id_tipoc", "nombre")
    search_fields = ("nombre",)
    ordering = ("nombre",)


# ----------------------------------------
# ADMIN Calendario
# ----------------------------------------
@admin.register(Calendario)
class CalendarioAdmin(admin.ModelAdmin):
    list_display = (
        "id_calendario",
        "titulo",
        "fecha",
        "hora_inicio",
        "hora_fin",
        "todo_el_dia",
        "id_tipoc",
        "id_usuario",
        "fecha_registro"
    )
    list_filter = ("id_tipoc", "id_usuario", "fecha", "todo_el_dia")
    search_fields = ("titulo", "descripcion")
    readonly_fields = ("fecha_registro",)
    ordering = ("-fecha", "-hora_inicio")

    fieldsets = (
        ("Información del Evento", {
            "fields": ("titulo", "descripcion", "fecha")
        }),
        ("Horario", {
            "fields": ("hora_inicio", "hora_fin", "todo_el_dia")
        }),
        ("Categorización", {
            "fields": ("id_tipoc", "id_usuario", "color")
        }),
        ("Registro", {
            "fields": ("fecha_registro",),
            "classes": ("collapse",)
        }),
    )


# ----------------------------------------
# ADMIN Avisos
# ----------------------------------------
@admin.register(Avisos)
class AvisosAdmin(admin.ModelAdmin):
    list_display = ("id_aviso", "titulo", "id_usuario", "fecha_registro")
    list_filter = ("id_usuario", "fecha_registro")
    search_fields = ("titulo", "descripcion")
    readonly_fields = ("fecha_registro",)
    ordering = ("-fecha_registro",)

    fieldsets = (
        ("Contenido del Aviso", {
            "fields": ("titulo", "descripcion")
        }),
        ("Metadatos", {
            "fields": ("id_usuario", "fecha_registro")
        }),
    )


# ----------------------------------------
# ADMIN Licencia
# ----------------------------------------
@admin.register(Licencia)
class LicenciaAdmin(admin.ModelAdmin):
    list_display = (
        "id_licencia",
        "id_usuario",
        "dia_inicio",
        "dia_fin",
        "fecha_registro"
    )
    list_filter = ("id_usuario", "dia_inicio", "dia_fin")
    search_fields = ("id_usuario__nombre",)
    readonly_fields = ("fecha_registro",)
    ordering = ("-fecha_registro",)

    fieldsets = (
        ("Información de la Licencia", {
            "fields": ("id_usuario", "dia_inicio", "dia_fin")
        }),
        ("Documentación", {
            "fields": ("imagen",)
        }),
        ("Registro", {
            "fields": ("fecha_registro",),
            "classes": ("collapse",)
        }),
    )


# ----------------------------------------
# ADMIN Perfil
# ----------------------------------------
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("id_perfil", "id_usuario", "fecha_registro")
    list_filter = ("fecha_registro",)
    search_fields = ("id_usuario__nombre", "descripcion")
    readonly_fields = ("fecha_registro",)
    ordering = ("-fecha_registro",)

    fieldsets = (
        ("Información del Perfil", {
            "fields": ("id_usuario", "foto_perfil", "descripcion")
        }),
        ("Registro", {
            "fields": ("fecha_registro",),
            "classes": ("collapse",)
        }),
    )


# ----------------------------------------
# ADMIN Documento
# ----------------------------------------
@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = (
        "id_documento",
        "nombre",
        "subido_por",
        "fecha_subida"
    )
    list_filter = ("subido_por", "fecha_subida")
    search_fields = ("nombre", "descripcion")
    readonly_fields = ("fecha_subida",)
    ordering = ("-fecha_subida",)

    fieldsets = (
        ("Información del Documento", {
            "fields": ("nombre", "descripcion", "archivo")
        }),
        ("Metadatos", {
            "fields": ("subido_por", "fecha_subida")
        }),
    )


# ----------------------------------------
# ADMIN InicioRegistrado
# ----------------------------------------
@admin.register(InicioRegistrado)
class InicioRegistradoAdmin(admin.ModelAdmin):
    list_display = ("id_inicio", "id_usuario", "fecha_registro")
    list_filter = ("id_usuario", "fecha_registro")
    search_fields = ("id_usuario__nombre",)
    readonly_fields = ("fecha_registro",)
    ordering = ("-fecha_registro",)

    fieldsets = (
        ("Registro de Inicio", {
            "fields": ("id_usuario", "fecha_registro")
        }),
    )


# ----------------------------------------
# ADMIN Mensajes
# ----------------------------------------
@admin.register(Mensajes)
class MensajesAdmin(admin.ModelAdmin):
    list_display = (
        "id_mensaje",
        "id_remitente",
        "id_destinatario",
        "fecha_envio",
        "leido"
    )
    list_filter = ("id_remitente", "id_destinatario", "fecha_envio", "leido")
    search_fields = ("cuerpo", "id_remitente__nombre", "id_destinatario__nombre")
    readonly_fields = ("fecha_envio",)
    ordering = ("-fecha_envio",)

    fieldsets = (
        ("Contenido del Mensaje", {
            "fields": ("cuerpo",)
        }),
        ("Destinatarios", {
            "fields": ("id_remitente", "id_destinatario")
        }),
        ("Estado", {
            "fields": ("leido", "fecha_envio")
        }),
    )
