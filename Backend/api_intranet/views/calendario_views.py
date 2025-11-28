# calendario_views.py - VERSIÓN CORREGIDA CON PERMISOS
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils.dateparse import parse_date
from api_intranet.models import Calendario, Usuario
import json

def get_usuario_actual(request):
    """Obtiene el usuario actual desde la sesión"""
    user_id = request.session.get("id_usuario")
    if not user_id:
        return None
    try:
        return Usuario.objects.get(id_usuario=user_id)
    except Usuario.DoesNotExist:
        return None

def tiene_permiso_edicion(usuario, evento):
    """Verifica si el usuario tiene permisos para editar/eliminar el evento"""
    if not usuario:
        return False
    
    rol_usuario = usuario.id_rol.nombre if usuario.id_rol else "Funcionario"
    
    # Director puede editar/eliminar todos los eventos
    if rol_usuario == "Director":
        return True
    
    # Funcionario solo puede editar sus propios eventos
    if rol_usuario == "Funcionario":
        return evento.id_usuario and evento.id_usuario.id_usuario == usuario.id_usuario
    
    return False

@require_http_methods(["GET", "POST"])
def eventos_api(request):
    """API para listar y crear eventos"""
    
    usuario = get_usuario_actual(request)
    if not usuario:
        return HttpResponseBadRequest('Usuario no autenticado')

    if request.method == 'GET':
        try:
            qs = Calendario.objects.select_related('id_usuario').all().order_by('fecha', 'hora_inicio')
            
            # Filtros de fecha
            start = request.GET.get('start')
            end = request.GET.get('end')
            
            if start:
                sd = parse_date(start)
                if sd:
                    qs = qs.filter(fecha__gte=sd)
            
            if end:
                ed = parse_date(end)
                if ed:
                    qs = qs.filter(fecha__lte=ed)

            # Serializar eventos
            data = []
            for evento in qs:
                data.append({
                    'id': evento.id_calendario,
                    'titulo': evento.titulo or '',
                    'fecha': evento.fecha.isoformat() if evento.fecha else '',
                    'hora_inicio': evento.hora_inicio.isoformat() if evento.hora_inicio else None,
                    'hora_fin': evento.hora_fin.isoformat() if evento.hora_fin else None,
                    'descripcion': evento.descripcion or '',
                    'color': evento.color or '#3A8DFF',
                    'todo_el_dia': evento.todo_el_dia,
                    'usuario_id': evento.id_usuario.id_usuario if evento.id_usuario else None,
                    'usuario_nombre': evento.id_usuario.nombre if evento.id_usuario else 'Sistema',
                    'puede_editar': tiene_permiso_edicion(usuario, evento)
                })
            
            return JsonResponse({'results': data}, status=200)
            
        except Exception as e:
            return HttpResponseBadRequest(f'Error al cargar eventos: {str(e)}')

    # POST - Crear nuevo evento
    elif request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return HttpResponseBadRequest('JSON inválido')

        titulo = payload.get('titulo', '').strip()
        fecha_str = payload.get('fecha')
        
        if not titulo:
            return HttpResponseBadRequest('El título es obligatorio')
        
        if not fecha_str:
            return HttpResponseBadRequest('La fecha es obligatoria')

        fecha = parse_date(fecha_str)
        if not fecha:
            return HttpResponseBadRequest('Formato de fecha inválido')

        try:
            evento = Calendario.objects.create(
                titulo=titulo,
                fecha=fecha,
                descripcion=payload.get('descripcion', ''),
                color=payload.get('color', '#3A8DFF'),
                todo_el_dia=payload.get('todo_el_dia', True),
                id_usuario=usuario
            )
            
            # Retornar el evento creado
            return JsonResponse({
                'id': evento.id_calendario,
                'titulo': evento.titulo,
                'fecha': evento.fecha.isoformat(),
                'descripcion': evento.descripcion,
                'color': evento.color,
                'usuario_id': usuario.id_usuario,
                'usuario_nombre': usuario.nombre,
                'puede_editar': True  # El creador siempre puede editar
            }, status=201)
            
        except Exception as e:
            return HttpResponseBadRequest(f'Error al crear evento: {str(e)}')

@require_http_methods(["GET", "PUT", "DELETE"])
def evento_detalle_api(request, id):
    """API para obtener, actualizar o eliminar un evento específico"""
    
    usuario = get_usuario_actual(request)
    if not usuario:
        return HttpResponseBadRequest('Usuario no autenticado')

    try:
        evento = Calendario.objects.get(id_calendario=id)
    except Calendario.DoesNotExist:
        return HttpResponseBadRequest('Evento no encontrado')

    # Verificar permisos
    if not tiene_permiso_edicion(usuario, evento):
        return HttpResponseBadRequest('No tienes permisos para esta acción')

    if request.method == 'GET':
        return JsonResponse({
            'id': evento.id_calendario,
            'titulo': evento.titulo,
            'fecha': evento.fecha.isoformat() if evento.fecha else '',
            'descripcion': evento.descripcion or '',
            'color': evento.color or '#3A8DFF',
            'usuario_id': evento.id_usuario.id_usuario if evento.id_usuario else None,
            'usuario_nombre': evento.id_usuario.nombre if evento.id_usuario else 'Sistema'
        })

    elif request.method == 'PUT':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return HttpResponseBadRequest('JSON inválido')

        # Actualizar campos permitidos
        if 'titulo' in payload:
            evento.titulo = payload['titulo'].strip()
        
        if 'fecha' in payload:
            fecha = parse_date(payload['fecha'])
            if fecha:
                evento.fecha = fecha
        
        if 'descripcion' in payload:
            evento.descripcion = payload['descripcion']
        
        if 'color' in payload:
            evento.color = payload['color']

        try:
            evento.save()
            return JsonResponse({
                'id': evento.id_calendario,
                'titulo': evento.titulo,
                'fecha': evento.fecha.isoformat(),
                'descripcion': evento.descripcion,
                'color': evento.color
            })
        except Exception as e:
            return HttpResponseBadRequest(f'Error al actualizar: {str(e)}')

    elif request.method == 'DELETE':
        try:
            evento.delete()
            return JsonResponse({'deleted': True, 'id': id})
        except Exception as e:
            return HttpResponseBadRequest(f'Error al eliminar: {str(e)}')