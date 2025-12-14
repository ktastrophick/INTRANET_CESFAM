##----------------------------------------------------------##
##  Modelos de la aplicación de intranet - VERSIÓN HÍBRIDA  ##
##  Compatible con views existentes + mejoras completas     ##
##----------------------------------------------------------##

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from datetime import date, timedelta
import re

class RolUsuario(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'rol_usuario'
        verbose_name = 'Rol de Usuario'
        verbose_name_plural = 'Roles de Usuario'
        
    def __str__(self) -> str:
        return self.nombre

class Cargo(models.Model):
    id_cargo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'cargo'
        
    def __str__(self) -> str:
        return self.nombre

class Departamento(models.Model):
    id_departamento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    jefe_departamento = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='jefe_departamento', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'departamento'
        
    def __str__(self) -> str:
        return self.nombre

class EstadoSolicitud(models.Model):
    id_estados = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'estado_solicitud'
        
    def __str__(self) -> str:
        return self.nombre

class TipoSolicitud(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'tipo_solicitud'
        
    def __str__(self) -> str:
        return self.nombre

class TipoCalendario(models.Model):
    id_tipoc = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tipo_calendario'
    
    def __str__(self) -> str:
        return self.nombre or f"Tipo {self.id_tipoc}"

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    rut = models.IntegerField()
    dv = models.CharField(max_length=1)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    correo = models.CharField(max_length=100, blank=True, null=True)
    contrasena = models.CharField(max_length=100)
    id_rol = models.ForeignKey(RolUsuario, models.DO_NOTHING, db_column='id_rol', blank=True, null=True)
    id_departamento = models.ForeignKey(Departamento, models.DO_NOTHING, db_column='id_departamento', blank=True, null=True)
    id_cargo = models.ForeignKey(Cargo, models.DO_NOTHING, db_column='id_cargo', blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'usuario'
    
    def __str__(self) -> str:
        return f"{self.rut}-{self.dv} | {self.nombre}"
    
    def clean(self) -> None:
        """Validaciones personalizadas del usuario"""
        super().clean()
        
        # Validar RUT chileno
        if not self.validar_rut_chileno(self.rut, self.dv):
            raise ValidationError({
                'rut': 'RUT inválido', 
                'dv': 'Dígito verificador incorrecto'
            })
        
        # Validar teléfono chileno
        if self.telefono:
            telefono_limpio = self.telefono.replace(' ', '').replace('-', '')
            patron = re.compile(r'^(\+56)?[2-9]\d{8}$')
            if not patron.match(telefono_limpio):
                raise ValidationError({
                    'telefono': 'Formato inválido. Ej: +56912345678 o 912345678'
                })
    
    @staticmethod
    def validar_rut_chileno(rut: int, dv: str) -> bool:
        """Valida RUT chileno con algoritmo módulo 11"""
        if not rut or not dv:
            return False
        
        rut_str = str(rut)
        dv = dv.upper().strip()
        
        # Validar formato básico
        if not rut_str.isdigit() or len(rut_str) < 7:
            return False
        
        if dv not in '0123456789K':
            return False
        
        # Algoritmo módulo 11
        suma = 0
        multiplo = 2
        
        for digito in reversed(rut_str):
            suma += int(digito) * multiplo
            multiplo += 1
            if multiplo > 7:
                multiplo = 2
        
        resto = suma % 11
        dv_calculado = 11 - resto
        
        if dv_calculado == 11:
            dv_calculado = '0'
        elif dv_calculado == 10:
            dv_calculado = 'K'
        else:
            dv_calculado = str(dv_calculado)
        
        return dv == dv_calculado
    
    @property
    def rut_completo(self) -> str:
        """Retorna el RUT completo formateado"""
        return f"{self.rut}-{self.dv}"
    
    def puede_aprobar_solicitudes(self) -> bool:
        return bool(
            self.id_rol and 
            self.id_rol.nombre in ['Director', 'Subdirector', 'Jefe_depto']
        )


class Avisos(models.Model):
    id_aviso = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'avisos'
        
    def __str__(self) -> str:
        return self.titulo or f"Aviso {self.id_aviso}"

class Calendario(models.Model):
    id_calendario = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=120, blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    id_tipoc = models.ForeignKey('TipoCalendario', models.DO_NOTHING, db_column='id_tipoc', blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True, help_text="Color en formato Hex (#3A8DFF)")
    todo_el_dia = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True, db_column='ubicacion')
    es_general = models.BooleanField(default=False, db_column='es_general')
    
    id_usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, db_column='id_usuario', null=True)
    id_tipoc = models.ForeignKey('TipoCalendario', on_delete=models.SET_NULL, null=True, blank=True, db_column='id_tipoc')

    class Meta:
        managed = True
        db_table = 'calendario'
        ordering =['fecha', 'hora_inicio']
        
    def __str__(self) -> str:
        return f"{self.titulo} - {self.fecha}" if self.titulo and self.fecha else f"Evento {self.id_calendario}"

class InicioRegistrado(models.Model):
    id_inicio = models.AutoField(primary_key=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'inicio_registrado'

class Licencia(models.Model):
    id_licencia = models.AutoField(primary_key=True)
    imagen = models.FileField(upload_to='licencias/')
    dia_inicio = models.DateField(blank=True, null=True)
    dia_fin = models.DateField(blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'licencia'

    def __str__(self) -> str:
        if self.id_usuario and self.dia_inicio and self.dia_fin:
            return f"Licencia de {self.id_usuario.nombre} ({self.dia_inicio} a {self.dia_fin})"
        return f"Licencia {self.id_licencia}"
    
    def clean(self) -> None:
        """Validaciones de licencia médica"""
        super().clean()
        
        # Validar fechas
        if self.dia_inicio and self.dia_fin:
            if self.dia_inicio > self.dia_fin:
                raise ValidationError({
                    'dia_inicio': 'Fecha de inicio debe ser anterior a fecha fin',
                    'dia_fin': 'Fecha fin debe ser posterior a fecha de inicio'
                })

class Mensajes(models.Model):
    id_mensaje = models.AutoField(primary_key=True)
    cuerpo = models.CharField(max_length=1000, blank=True, null=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    leido = models.IntegerField(blank=True, null=True)
    id_remitente = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_remitente', blank=True, null=True)
    id_destinatario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_destinatario', related_name='mensajes_id_destinatario_set', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'mensajes'

class Solicitud(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    dia_inicio = models.DateField(blank=True, null=True)
    dia_fin = models.DateField(blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    tipo_solicitud = models.ForeignKey('TipoSolicitud', models.DO_NOTHING, db_column='tipo_solicitud', blank=True, null=True)
    estado_solicitud = models.ForeignKey(EstadoSolicitud, models.DO_NOTHING, db_column='estado_solicitud', blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    aprobacion_jefe = models.BooleanField(null=True, blank=True)
    aprobacion_director = models.BooleanField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'solicitud'
        
    def __str__(self) -> str:
        tipo_nombre = self.tipo_solicitud.nombre if self.tipo_solicitud else "Sin tipo"
        return f"Solicitud {self.id_solicitud} - {tipo_nombre}"
    
    def clean(self) -> None:
        """Validaciones de coherencia de fechas"""
        super().clean()
        
        # Validar que fecha inicio sea anterior a fecha fin
        if self.dia_inicio and self.dia_fin:
            if self.dia_inicio > self.dia_fin:
                raise ValidationError({
                    'dia_inicio': 'La fecha de inicio debe ser anterior a la fecha fin',
                    'dia_fin': 'La fecha fin debe ser posterior a la fecha de inicio'
                })
            
            # Validar que no sea en el pasado
            if self.dia_inicio < date.today():
                raise ValidationError({
                    'dia_inicio': 'No se pueden solicitar permisos en fechas pasadas'
                })

class Perfil(models.Model):
    id_perfil = models.AutoField(primary_key=True)
    foto_perfil = models.ImageField(
        upload_to='perfiles/',  # Cambiado de CharField a ImageField
        blank=True, 
        null=True,
        max_length=255
    )
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    id_usuario = models.ForeignKey(
        'Usuario', 
        on_delete=models.CASCADE, 
        db_column='id_usuario', 
        blank=True, 
        null=True
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'perfil'

    def __str__(self):
        return f"Perfil de {self.id_usuario.nombre if self.id_usuario else 'Sin usuario'}"

    def clean(self):
        """Validaciones del perfil"""
        super().clean()
        
        # Validar tamaño máximo de foto (5MB)
        if self.foto_perfil and hasattr(self.foto_perfil, 'size'):
            if self.foto_perfil.size > 5 * 1024 * 1024:
                raise ValidationError({
                    'foto_perfil': 'La imagen no puede superar 5MB'
                })

class Documento(models.Model):
    id_documento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to='documentos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'api_intranet_documento'

    def __str__(self):
        return self.nombre
    
    def clean(self) -> None:
        """Validaciones de documento"""
        super().clean()
        
        # Validar tamaño máximo (10MB)
        if self.archivo and self.archivo.size > 10 * 1024 * 1024:
            raise ValidationError({
                'archivo': 'El archivo no puede superar 10MB'
            })

# Métodos adicionales para compatibilidad con views existentes
def get_usuario_actual(request):
    """Función auxiliar para compatibilidad con views existentes"""
    user_id = request.session.get("id_usuario")
    if not user_id:
        return None
    try:
        return Usuario.objects.get(id_usuario=user_id)
    except Usuario.DoesNotExist:
        return None