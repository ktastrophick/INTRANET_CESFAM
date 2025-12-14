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
from django.db.models import Q
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
    ubicacion: str | None
    es_general: bool


def calendario(request: HttpRequest) -> HttpResponse:
    """Vista principal del calendario"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")
    
    rol_usuario = usuario.id_rol.nombre if usuario.id_rol else "Funcionario"
    eventos = Calendario.objects.all().order_by('fecha', 'hora_inicio')
    tipos_evento = TipoCalendario.objects.all()
    
    return render(request, 'pages/calendario.html', {
        "usuario": usuario,
        "rol_usuario": rol_usuario,
        "eventos": eventos,
        "tipos_evento": tipos_evento
    })

def _serialize_event(e: Calendario) -> EventoJSON:
    """Serializa un objeto Calendario a JSON"""
    # Usar el campo es_general directamente de la DB
    es_general = getattr(e, 'es_general', False)
    
    return {
        'id': e.id_calendario,
        'titulo': e.titulo,
        'fecha': e.fecha.isoformat() if e.fecha else '',
        'hora_inicio': e.hora_inicio.isoformat() if e.hora_inicio else None,
        'hora_fin': e.hora_fin.isoformat() if e.hora_fin else None,
        'descripcion': e.descripcion or '',
        'ubicacion': getattr(e, 'ubicacion', '') or '',
        'color': e.color or ('#FF6B6B' if es_general else '#3A8DFF'),
        'tipo_id': getattr(e.id_tipoc, 'id_tipoc', None) if e.id_tipoc else None,
        'usuario_id': getattr(e.id_usuario, 'id_usuario', None) if e.id_usuario else None,
        'usuario_nombre': e.id_usuario.nombre if e.id_usuario else '',
        'todo_el_dia': e.todo_el_dia,
        'es_general': es_general,
        'editable': True,  # Todos pueden editar sus propios eventos
    }

@require_http_methods(["GET"])
def tipos_evento_api(request: HttpRequest) -> JsonResponse:
    """API para obtener tipos de evento del calendario"""
    tipos = TipoCalendario.objects.all()
    data = [
        {
            'id': t.id_tipoc,
            'nombre': t.nombre,
            'color': '#FF6B6B' if t.nombre == 'General' else '#3A8DFF'
        }
        for t in tipos
    ]
    return JsonResponse({'results': data}, status=200)

@require_http_methods(["GET", "POST"])
def eventos_api(request: HttpRequest) -> Union[JsonResponse, HttpResponseBadRequest]:
    """API para listar y crear eventos del calendario"""
    
    if request.method == 'GET':
        usuario = get_usuario_actual(request)
        
        if usuario:
            # Director ve: sus eventos (personales y generales que creó) + eventos generales de otros
            if usuario.id_rol and usuario.id_rol.nombre in ['Director']:
                qs = Calendario.objects.filter(
                    Q(id_usuario=usuario) |  # Sus propios eventos (personales y generales)
                    Q(es_general=True)  # Todos los eventos generales
                ).distinct()
            # Admin ve todos los eventos
            elif usuario.id_rol and usuario.id_rol.nombre == 'Admin':
                qs = Calendario.objects.all()
            # Funcionarios ven: sus eventos personales + eventos generales de todos
            else:
                qs = Calendario.objects.filter(
                    Q(id_usuario=usuario, es_general=False) |  # Sus eventos personales
                    Q(es_general=True)  # Eventos generales de todos
                ).distinct()
        else:
            return JsonResponse({'results': []}, status=200)
        
        qs = qs.order_by('fecha', 'hora_inicio')
        
        # Filtros de fecha
        start: str | None = request.GET.get('start')
        end: str | None = request.GET.get('end')
        
        if start:
            sd = parse_date(start)
            if sd:
                qs = qs.filter(fecha__gte=sd)
        
        if end:
            ed = parse_date(end)
            if ed:
                qs = qs.filter(fecha__lte=ed)

        data: List[EventoJSON] = [_serialize_event(e) for e in qs]
        return JsonResponse({'results': data}, status=200)
    
    # POST - Crear nuevo evento
    try:
        payload: Dict[str, Any] = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('JSON inválido en el cuerpo de la petición')
    
    usuario = get_usuario_actual(request)
    if not usuario:
        return HttpResponseBadRequest('Usuario no autenticado')
    
    # Validar campos requeridos
    titulo = payload.get('titulo')
    fecha_str = payload.get('fecha')
    
    if not (isinstance(titulo, str) and titulo.strip()):
        return HttpResponseBadRequest('Campo titulo es requerido y no puede estar vacío')
    
    if not isinstance(fecha_str, str):
        return HttpResponseBadRequest('Campo fecha es requerido')
    
    fecha = parse_date(fecha_str)
    if not fecha:
        return HttpResponseBadRequest('Formato de fecha inválido. Use YYYY-MM-DD')
    
    # Verificar si es todo el día
    todo_el_dia = bool(payload.get('todo_el_dia', False))
    
    # Parsear horas (solo si NO es todo el día)
    hora_inicio = None
    hora_fin = None
    
    if not todo_el_dia:
        hora_inicio_str = payload.get('hora_inicio')
        hora_fin_str = payload.get('hora_fin')
        
        if not hora_inicio_str or not hora_fin_str:
            return HttpResponseBadRequest('Para eventos no de todo el día, las horas de inicio y fin son obligatorias')
        
        hora_inicio = parse_time(hora_inicio_str)
        hora_fin = parse_time(hora_fin_str)
        
        if not hora_inicio or not hora_fin:
            return HttpResponseBadRequest('Formato de hora inválido')
        
        # Validar que hora_fin sea posterior a hora_inicio
        if hora_inicio >= hora_fin:
            return HttpResponseBadRequest('La hora de fin debe ser posterior a la hora de inicio')
    
    # Determinar si es evento general
    es_general = payload.get('es_general', False)
    
    # Solo Director puede crear eventos generales
    if es_general and (not usuario.id_rol or usuario.id_rol.nombre != 'Director'):
        return HttpResponseBadRequest('Solo el Director puede crear eventos generales')
    
    # Determinar color
    if es_general:
        color = '#FF6B6B'  # Rojo para eventos generales
    else:
        color = str(payload.get('color') or '#3A8DFF')
    
    try:
        evento = Calendario.objects.create(
            titulo=titulo.strip(),
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            descripcion=str(payload.get('descripcion') or ''),
            ubicacion=str(payload.get('ubicacion') or ''),
            color=color,
            todo_el_dia=todo_el_dia,
            es_general=es_general,
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
    usuario = get_usuario_actual(request)
    
    if not usuario:
        return HttpResponseBadRequest('Usuario no autenticado')
    
    # Verificar permisos
    es_general = getattr(evento, 'es_general', False)
    usuario_es_propietario = (evento.id_usuario and 
                              evento.id_usuario.id_usuario == usuario.id_usuario)
    usuario_es_admin = (usuario.id_rol and usuario.id_rol.nombre == 'Admin')
    
    # Para VER: eventos generales todos pueden verlos, personales solo el dueño
    if not es_general and not usuario_es_propietario and not usuario_es_admin:
        return HttpResponseBadRequest('No tienes permisos para ver este evento')
    
    if request.method == 'GET':
        return JsonResponse(_serialize_event(evento), status=200)

    # Para MODIFICAR/ELIMINAR: solo el propietario o admin
    if not usuario_es_propietario and not usuario_es_admin:
        return HttpResponseBadRequest('No tienes permisos para modificar este evento')

    if request.method == 'PUT':
        try:
            payload: Dict[str, Any] = json.loads(request.body.decode('utf-8'))
        except Exception:
            return HttpResponseBadRequest('JSON inválido en el cuerpo de la petición')

        titulo = payload.get('titulo')
        fecha_str = payload.get('fecha')
        
        if not (isinstance(titulo, str) and titulo.strip()):
            return HttpResponseBadRequest('Campo titulo es requerido y no puede estar vacío')
        
        if not isinstance(fecha_str, str):
            return HttpResponseBadRequest('Campo fecha es requerido')

        fecha = parse_date(fecha_str)
        if not fecha:
            return HttpResponseBadRequest('Formato de fecha inválido. Use YYYY-MM-DD')

        # Verificar si es todo el día
        todo_el_dia = bool(payload.get('todo_el_dia', False))
        
        hora_inicio = None
        hora_fin = None
        
        if not todo_el_dia:
            hora_inicio_str = payload.get('hora_inicio')
            hora_fin_str = payload.get('hora_fin')
            
            if not hora_inicio_str or not hora_fin_str:
                return HttpResponseBadRequest('Para eventos no de todo el día, las horas son obligatorias')
            
            hora_inicio = parse_time(hora_inicio_str)
            hora_fin = parse_time(hora_fin_str)
            
            if not hora_inicio or not hora_fin:
                return HttpResponseBadRequest('Formato de hora inválido')
            
            if hora_inicio >= hora_fin:
                return HttpResponseBadRequest('La hora de fin debe ser posterior a la hora de inicio')

        # Verificar cambio de tipo de evento
        es_general_nuevo = payload.get('es_general', False)
        if es_general_nuevo and (not usuario.id_rol or usuario.id_rol.nombre != 'Director'):
            return HttpResponseBadRequest('Solo el Director puede crear eventos generales')

        # Actualizar evento
        evento.titulo = titulo.strip()
        evento.fecha = fecha
        evento.hora_inicio = hora_inicio
        evento.hora_fin = hora_fin
        evento.descripcion = str(payload.get('descripcion') or '')
        evento.ubicacion = str(payload.get('ubicacion') or '')
        evento.todo_el_dia = todo_el_dia
        evento.es_general = es_general_nuevo
        
        # Actualizar color según tipo
        if es_general_nuevo:
            evento.color = '#FF6B6B'
        else:
            evento.color = str(payload.get('color') or '#3A8DFF')
        
        try:
            evento.full_clean()
            evento.save()
            return JsonResponse(_serialize_event(evento), status=200)
        except Exception as e:
            return HttpResponseBadRequest(f'Error de validación: {str(e)}')

    # DELETE
    try:
        evento.delete()
        return JsonResponse({'deleted': True, 'id': id}, status=200)
    except Exception as e:
        return HttpResponseBadRequest(f'Error al eliminar evento: {str(e)}')