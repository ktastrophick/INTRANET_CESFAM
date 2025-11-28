# api_intranet/views/calendario_views.py
from __future__ import annotations

from typing import Any, Dict, List, TypedDict, Union, Optional
from django.shortcuts import render, get_object_or_404
from django.http import (
    HttpRequest, HttpResponse, JsonResponse, HttpResponseBadRequest
)
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_date, parse_time
from api_intranet.models import Calendario, TipoCalendario, Usuario
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json

def get_usuario_actual(request: HttpRequest) -> Optional[Usuario]:
    """Obtiene el usuario actual desde la sesión"""
    user_id = request.session.get("id_usuario")
    if not user_id:
        return None
    try:
        return Usuario.objects.get(id_usuario=user_id)
    except Usuario.DoesNotExist:
        return None

# ---- Tipos auxiliares ----
class EventoJSON(TypedDict, total=False):
    id: int
    titulo: str
    fecha: str
    hora_inicio: str | None
    hora_fin: str | None
    descripcion: str
    color: str
    tipo_id: int | None
    usuario_id: int | None
    todo_el_dia: bool


def calendario(request: HttpRequest) -> HttpResponse:
    """Vista principal del calendario"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")
    
    # Obtener todos los eventos ordenados por fecha
    eventos = Calendario.objects.all().order_by('fecha', 'hora_inicio')
    
    # También obtener tipos de calendario si los necesitas
    tipos_evento = TipoCalendario.objects.all()
    
    return render(request, 'pages/calendario.html', {
        "usuario": usuario,
        "eventos": eventos,
        "tipos_evento": tipos_evento
    })

def _serialize_event(e: Calendario) -> EventoJSON:
    """Serializa un objeto Calendario a JSON para FullCalendar"""
    return {
        'id': e.id_calendario,
        'titulo': e.titulo,
        'fecha': e.fecha.isoformat() if e.fecha else '',
        'hora_inicio': e.hora_inicio.isoformat() if e.hora_inicio else None,
        'hora_fin': e.hora_fin.isoformat() if e.hora_fin else None,
        'descripcion': e.descripcion or '',
        'color': e.color or '#3A8DFF',
        'tipo_id': getattr(e.id_tipoc, 'id_tipoc', None),
        'usuario_id': getattr(e.id_usuario, 'id_usuario', None),
        'todo_el_dia': e.todo_el_dia
    }

@require_http_methods(["GET", "POST"])
def eventos_api(request: HttpRequest) -> Union[JsonResponse, HttpResponseBadRequest]:
    """API para listar y crear eventos del calendario"""
    
    if request.method == 'GET':
        # Obtener eventos con filtros de fecha
        qs = Calendario.objects.all().order_by('fecha', 'hora_inicio')
        start: str | None = request.GET.get('start')
        end: str | None = request.GET.get('end')
        
        if start:
            sd = parse_date(start)
            if not sd:
                return HttpResponseBadRequest('Parámetro start inválido')
            qs = qs.filter(fecha__gte=sd)
        
        if end:
            ed = parse_date(end)
            if not ed:
                return HttpResponseBadRequest('Parámetro end inválido')
            qs = qs.filter(fecha__lte=ed)

        data: List[EventoJSON] = [_serialize_event(e) for e in qs]
        return JsonResponse({'results': data}, status=200)

    # POST - Crear nuevo evento
    try:
        payload: Dict[str, Any] = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('JSON inválido en el cuerpo de la petición')

    # Validar campos requeridos
    titulo = payload.get('titulo')
    fecha_str = payload.get('fecha')
    
    if not (isinstance(titulo, str) and titulo.strip()):
        return HttpResponseBadRequest('Campo titulo es requerido y no puede estar vacío')
    
    if not isinstance(fecha_str, str):
        return HttpResponseBadRequest('Campo fecha es requerido')

    # Parsear fecha
    fecha = parse_date(fecha_str)
    if not fecha:
        return HttpResponseBadRequest('Formato de fecha inválido. Use YYYY-MM-DD')

    # Parsear horas opcionales
    hora_inicio = None
    hora_fin = None
    hora_inicio_str = payload.get('hora_inicio')
    hora_fin_str = payload.get('hora_fin')
    
    if hora_inicio_str:
        hora_inicio = parse_time(hora_inicio_str)
    
    if hora_fin_str:
        hora_fin = parse_time(hora_fin_str)

    # Validar que hora_fin sea posterior a hora_inicio si ambas están presentes
    if hora_inicio and hora_fin and hora_inicio >= hora_fin:
        return HttpResponseBadRequest('La hora de fin debe ser posterior a la hora de inicio')

    # Obtener usuario actual para asociar el evento
    usuario = get_usuario_actual(request)
    
    # Crear el evento
    try:
        evento = Calendario.objects.create(
            titulo=titulo.strip(),
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            descripcion=str(payload.get('descripcion') or ''),
            color=str(payload.get('color') or '#3A8DFF'),
            todo_el_dia=bool(payload.get('todo_el_dia', False)),
            id_usuario=usuario
        )
        
        return JsonResponse(_serialize_event(evento), status=201)
    except Exception as e:
        return HttpResponseBadRequest(f'Error al crear evento: {str(e)}')

@require_http_methods(["GET", "PUT", "DELETE"])
def evento_detalle_api(
    request: HttpRequest, id: int
) -> Union[JsonResponse, HttpResponseBadRequest]:
    """API para obtener, actualizar o eliminar un evento específico"""
    
    evento = get_object_or_404(Calendario, id_calendario=id)

    # Verificar permisos (solo el usuario que creó el evento o admin puede modificarlo)
    usuario = get_usuario_actual(request)
    if not usuario:
        return HttpResponseBadRequest('Usuario no autenticado')
    usuario_tiene_permiso = (
        evento.id_usuario and
        getattr(evento.id_usuario, 'id_usuario', None) == getattr(usuario, 'id_usuario', None)
    )
    es_admin =(
        usuario.id_rol and
        getattr(usuario.id_rol, 'nombre', '') == 'Admin'
    )
    
    if not (usuario_tiene_permiso or es_admin):
        return HttpResponseBadRequest('No tienes permisos para ver este evento')
    
    if (evento.id_usuario and evento.id_usuario.id_usuario != usuario.id_usuario and 
        not (usuario.id_rol and usuario.id_rol.nombre == 'Admin')):
        return HttpResponseBadRequest('No tienes permisos para modificar este evento')

    if request.method == 'GET':
        return JsonResponse(_serialize_event(evento), status=200)

    if request.method == 'PUT':
        try:
            payload: Dict[str, Any] = json.loads(request.body.decode('utf-8'))
        except Exception:
            return HttpResponseBadRequest('JSON inválido en el cuerpo de la petición')

        # Validar campos requeridos
        titulo = payload.get('titulo')
        fecha_str = payload.get('fecha')
        
        if not (isinstance(titulo, str) and titulo.strip()):
            return HttpResponseBadRequest('Campo titulo es requerido y no puede estar vacío')
        
        if not isinstance(fecha_str, str):
            return HttpResponseBadRequest('Campo fecha es requerido')

        # Parsear fecha
        fecha = parse_date(fecha_str)
        if not fecha:
            return HttpResponseBadRequest('Formato de fecha inválido. Use YYYY-MM-DD')

        # Parsear horas opcionales
        hora_inicio = None
        hora_fin = None
        hora_inicio_str = payload.get('hora_inicio')
        hora_fin_str = payload.get('hora_fin')
        
        if hora_inicio_str:
            hora_inicio = parse_time(hora_inicio_str)
        
        if hora_fin_str:
            hora_fin = parse_time(hora_fin_str)

        # Validar que hora_fin sea posterior a hora_inicio si ambas están presentes
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            return HttpResponseBadRequest('La hora de fin debe ser posterior a la hora de inicio')

        # Actualizar el evento
        evento.titulo = titulo.strip()
        evento.fecha = fecha
        evento.hora_inicio = hora_inicio
        evento.hora_fin = hora_fin
        evento.descripcion = str(payload.get('descripcion') or '')
        evento.color = str(payload.get('color') or '#3A8DFF')
        evento.todo_el_dia = bool(payload.get('todo_el_dia', False))
        
        try:
            evento.full_clean()  # Aplicar validaciones del modelo
            evento.save()
            return JsonResponse(_serialize_event(evento), status=200)
        except Exception as e:
            return HttpResponseBadRequest(f'Error de validación: {str(e)}')

    # DELETE - Eliminar evento
    try:
        evento.delete()
        return JsonResponse({'deleted': True, 'id': id}, status=200)
    except Exception as e:
        return HttpResponseBadRequest(f'Error al eliminar evento: {str(e)}')