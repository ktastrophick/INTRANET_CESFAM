# api_intranet/views/calendario_views.py
from __future__ import annotations

from typing import Any, Dict, List, TypedDict, Union
from django.shortcuts import render, get_object_or_404
from django.http import (
    HttpRequest, HttpResponse, JsonResponse, HttpResponseBadRequest
)
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_date
from api_intranet.models import Evento  # Import absoluto robusto
import json

# ---- Tipos auxiliares ----
class EventoJSON(TypedDict, total=False):
    id: int
    titulo: str
    fecha: str
    descripcion: str
    color: str
    tipo_id: int | None
    usuario_id: int | None

def calendario(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/calendario.html')

def _serialize_event(e: Evento) -> EventoJSON:
    return {
        'id': e.id_evento,
        'titulo': e.titulo,
        'fecha': e.fecha.isoformat(),
        'descripcion': e.descripcion or '',
        'color': e.color or '#3A8DFF',
        'tipo_id': getattr(e.tipo, 'id_tipoc', None),
        'usuario_id': getattr(e.usuario, 'id_usuario', None),
    }

@require_http_methods(["GET", "POST"])
def eventos_api(request: HttpRequest) -> Union[JsonResponse, HttpResponseBadRequest]:
    if request.method == 'GET':
        qs = Evento.objects.all().order_by('fecha')
        start: str | None = request.GET.get('start')
        end: str | None = request.GET.get('end')
        if start:
            sd = parse_date(start)
            if not sd:
                return HttpResponseBadRequest('start inválido')
            qs = qs.filter(fecha__gte=sd)
        if end:
            ed = parse_date(end)
            if not ed:
                return HttpResponseBadRequest('end inválido')
            qs = qs.filter(fecha__lte=ed)

        data: List[EventoJSON] = [_serialize_event(e) for e in qs]
        return JsonResponse({'results': data}, status=200)

    # POST crear
    try:
        payload: Dict[str, Any] = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('JSON inválido')

    titulo = payload.get('titulo')
    fecha_str = payload.get('fecha')
    if not (isinstance(titulo, str) and isinstance(fecha_str, str)):
        return HttpResponseBadRequest('Campos requeridos: titulo, fecha')

    f = parse_date(fecha_str)
    if not f:
        return HttpResponseBadRequest('Fecha inválida')

    e = Evento.objects.create(
        titulo=titulo,
        fecha=f,
        descripcion=str(payload.get('descripcion') or ''),
        color=str(payload.get('color') or '#3A8DFF')
    )
    return JsonResponse(_serialize_event(e), status=201)

@require_http_methods(["GET", "PUT", "DELETE"])
def evento_detalle_api(
    request: HttpRequest, id: int
) -> Union[JsonResponse, HttpResponseBadRequest]:
    e = get_object_or_404(Evento, pk=id)

    if request.method == 'GET':
        return JsonResponse(_serialize_event(e), status=200)

    if request.method == 'PUT':
        try:
            payload: Dict[str, Any] = json.loads(request.body.decode('utf-8'))
        except Exception:
            return HttpResponseBadRequest('JSON inválido')

        titulo = payload.get('titulo')
        fecha_str = payload.get('fecha')
        if not (isinstance(titulo, str) and isinstance(fecha_str, str)):
            return HttpResponseBadRequest('Campos requeridos: titulo, fecha')

        f = parse_date(fecha_str)
        if not f:
            return HttpResponseBadRequest('Fecha inválida')

        e.titulo = titulo
        e.fecha = f
        e.descripcion = str(payload.get('descripcion') or '')
        e.color = str(payload.get('color') or '#3A8DFF')
        e.save()
        return JsonResponse(_serialize_event(e), status=200)

    # DELETE
    e.delete()
    return JsonResponse({'deleted': True}, status=200)
