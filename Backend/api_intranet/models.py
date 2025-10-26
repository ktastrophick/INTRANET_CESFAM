# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Avisos(models.Model):
    id_aviso = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'avisos'


class Calendario(models.Model):
    id_calendario = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=300, blank=True, null=True)
    id_tipoc = models.ForeignKey('TipoCalendario', models.DO_NOTHING, db_column='id_tipoc', blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'calendario'


class Cargo(models.Model):
    id_cargo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'cargo'


class Departamento(models.Model):
    id_departamento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    jefe_departamento = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='jefe_departamento', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'departamento'


class EstadoSolicitud(models.Model):
    id_estados = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'estado_solicitud'


class InicioRegistrado(models.Model):
    id_inicio = models.AutoField(primary_key=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'inicio_registrado'


class Licencia(models.Model):
    id_licencia = models.AutoField(primary_key=True)
    imagen = models.CharField(max_length=255, blank=True, null=True)
    dia_inicio = models.DateField(blank=True, null=True)
    dia_fin = models.DateField(blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'licencia'


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


class RolUsuario(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'rol_usuario'


class Solicitud(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    dia_inicio = models.DateField(blank=True, null=True)
    dia_fin = models.DateField(blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    tipo_solicitud = models.ForeignKey('TipoSolicitud', models.DO_NOTHING, db_column='tipo_solicitud', blank=True, null=True)
    estado_solicitud = models.ForeignKey(EstadoSolicitud, models.DO_NOTHING, db_column='estado_solicitud', blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'solicitud'


class TipoCalendario(models.Model):
    id_tipoc = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tipo_calendario'


class TipoSolicitud(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'tipo_solicitud'


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

class Perfil(models.Model):
    id_perfil = models.AutoField(primary_key=True)
    foto_perfil = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, db_column='id_usuario', blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'perfil'
