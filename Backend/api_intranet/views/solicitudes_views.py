from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from api_intranet.models import Solicitud, TipoSolicitud, EstadoSolicitud, Usuario
from django.utils import timezone
from typing import Optional
from datetime import date

def get_usuario_actual(request: HttpRequest) -> Optional[Usuario]:
    """Obtiene el usuario actual desde la sesión"""
    user_id = request.session.get("id_usuario")
    if not user_id:
        return None
    try:
        return Usuario.objects.get(id_usuario=user_id)
    except Usuario.DoesNotExist:
        return None


def lista_solicitudes(request: HttpRequest) -> HttpResponse:
    """Lista de solicitudes según el rol del usuario"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    rol = usuario.id_rol.nombre if usuario.id_rol else "Funcionario"

    if rol == "Funcionario":
        # Funcionario ve solo sus propias solicitudes
        solicitudes = Solicitud.objects.filter(id_usuario=usuario)
    elif rol == "Jefe de Departamento":
        # Jefe ve solicitudes de su departamento
        if usuario.id_departamento:
            solicitudes = Solicitud.objects.filter(
                id_usuario__id_departamento=usuario.id_departamento
            )
        else:
            solicitudes = Solicitud.objects.none()
    elif rol == "Admin" or rol == "Director":
        # Admin/Director ve todas las solicitudes
        solicitudes = Solicitud.objects.all()
    else:
        solicitudes = Solicitud.objects.filter(id_usuario=usuario)

    # Ordenar por fecha más reciente primero
    solicitudes = solicitudes.select_related(
        'id_usuario', 'tipo_solicitud', 'estado_solicitud'
    ).order_by('-fecha_registro')

    context = {
        "solicitudes": solicitudes,
        "usuario": usuario,
        "rol": rol
    }
    return render(request, "pages/solicitudes/lista_solicitudes.html", context)


def aprobar_jefe(request: HttpRequest, id_solicitud: int) -> HttpResponse:
    """Jefe de departamento aprueba una solicitud"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    # Verificar que sea jefe de departamento
    if not usuario.puede_aprobar_solicitudes() or usuario.id_rol.nombre != "Jefe de Departamento":
        messages.error(request, "No tienes permisos para aprobar solicitudes.")
        return redirect("lista_solicitudes")

    solicitud = get_object_or_404(Solicitud, id_solicitud=id_solicitud)

    # Verificar que la solicitud sea de su departamento
    if solicitud.id_usuario.id_departamento != usuario.id_departamento:
        messages.error(request, "Solo puedes aprobar solicitudes de tu departamento.")
        return redirect("lista_solicitudes")

    if solicitud.aprobacion_jefe is not None:
        messages.error(request, "Esta solicitud ya fue revisada por el jefe.")
        return redirect("lista_solicitudes")

    try:
        solicitud.aprobacion_jefe = True
        # Si también necesita aprobación del director, mantener estado pendiente
        if solicitud.aprobacion_director is None:
            estado_pendiente = EstadoSolicitud.objects.get(nombre="Pendiente")
            solicitud.estado_solicitud = estado_pendiente
        solicitud.save()
        messages.success(request, "Solicitud aprobada y enviada al Director.")
    except Exception as e:
        messages.error(request, f"Error al aprobar la solicitud: {str(e)}")

    return redirect("lista_solicitudes")


def rechazar_jefe(request: HttpRequest, id_solicitud: int) -> HttpResponse:
    """Jefe de departamento rechaza una solicitud"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    # Verificar que sea jefe de departamento
    if not usuario.puede_aprobar_solicitudes() or usuario.id_rol.nombre != "Jefe de Departamento":
        messages.error(request, "No tienes permisos para rechazar solicitudes.")
        return redirect("lista_solicitudes")

    solicitud = get_object_or_404(Solicitud, id_solicitud=id_solicitud)

    # Verificar que la solicitud sea de su departamento
    if solicitud.id_usuario.id_departamento != usuario.id_departamento:
        messages.error(request, "Solo puedes rechazar solicitudes de tu departamento.")
        return redirect("lista_solicitudes")

    if solicitud.aprobacion_jefe is not None:
        messages.error(request, "Esta solicitud ya fue revisada por el jefe.")
        return redirect("lista_solicitudes")

    try:
        solicitud.aprobacion_jefe = False
        estado_rechazado = EstadoSolicitud.objects.get(nombre="Rechazada")
        solicitud.estado_solicitud = estado_rechazado
        solicitud.save()
        messages.success(request, "Solicitud rechazada.")
    except Exception as e:
        messages.error(request, f"Error al rechazar la solicitud: {str(e)}")

    return redirect("lista_solicitudes")


def aprobar_director(request: HttpRequest, id_solicitud: int) -> HttpResponse:
    """Director aprueba una solicitud"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    # Verificar que sea director o admin
    if usuario.id_rol.nombre not in ["Admin", "Director"]:
        messages.error(request, "No tienes permisos para aprobar solicitudes como director.")
        return redirect("lista_solicitudes")

    solicitud = get_object_or_404(Solicitud, id_solicitud=id_solicitud)

    if solicitud.aprobacion_director is not None:
        messages.error(request, "Esta solicitud ya fue revisada por el director.")
        return redirect("lista_solicitudes")

    try:
        solicitud.aprobacion_director = True
        
        # Si jefe aprobó y director aprueba → estado final aprobado
        if solicitud.aprobacion_jefe and solicitud.aprobacion_director:
            estado_aprobado = EstadoSolicitud.objects.get(nombre="Aprobada")
            solicitud.estado_solicitud = estado_aprobado
        
        solicitud.save()
        messages.success(request, "Solicitud aprobada completamente.")
    except Exception as e:
        messages.error(request, f"Error al aprobar la solicitud: {str(e)}")

    return redirect("lista_solicitudes")


def rechazar_director(request: HttpRequest, id_solicitud: int) -> HttpResponse:
    """Director rechaza una solicitud"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    # Verificar que sea director o admin
    if usuario.id_rol.nombre not in ["Admin", "Director"]:
        messages.error(request, "No tienes permisos para rechazar solicitudes como director.")
        return redirect("lista_solicitudes")

    solicitud = get_object_or_404(Solicitud, id_solicitud=id_solicitud)

    if solicitud.aprobacion_director is not None:
        messages.error(request, "Esta solicitud ya fue revisada por el director.")
        return redirect("lista_solicitudes")

    try:
        solicitud.aprobacion_director = False
        estado_rechazado = EstadoSolicitud.objects.get(nombre="Rechazada")
        solicitud.estado_solicitud = estado_rechazado
        solicitud.save()
        messages.success(request, "Solicitud rechazada por el Director.")
    except Exception as e:
        messages.error(request, f"Error al rechazar la solicitud: {str(e)}")

    return redirect("lista_solicitudes")


def form_solicitud(request: HttpRequest) -> HttpResponse:
    """Crear nueva solicitud"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    # Obtener tipos de solicitud (siempre disponible)
    tipos_solicitud = TipoSolicitud.objects.all()
    estado_pendiente = EstadoSolicitud.objects.get(nombre="Pendiente")

    if request.method == "POST":
        tipo_id = request.POST.get("tipo_solicitud")
        fecha_inicio = request.POST.get("dia_inicio")
        fecha_fin = request.POST.get("dia_fin")

        print(f"DEBUG POST: tipo_id={tipo_id}, fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}")

        # Validaciones básicas
        if not tipo_id or not fecha_inicio or not fecha_fin:
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, "pages/solicitudes/form_solicitud.html", {
                "tipos_solicitud": tipos_solicitud,
                "data": {
                    "tipo_solicitud": tipo_id,
                    "dia_inicio": fecha_inicio,
                    "dia_fin": fecha_fin
                },
                "today": date.today()
            })

        try:
            # Obtener el objeto TipoSolicitud
            tipo_solicitud_obj = TipoSolicitud.objects.get(id_tipo=tipo_id)
            
            # Crear la solicitud con todos los campos requeridos
            solicitud = Solicitud(
                dia_inicio=fecha_inicio,
                dia_fin=fecha_fin,
                tipo_solicitud=tipo_solicitud_obj,
                id_usuario=usuario,
                estado_solicitud=estado_pendiente,
                fecha_registro=timezone.now(),
                aprobacion_jefe=None,
                aprobacion_director=None
            )
            
            print(f"DEBUG: Creando solicitud para usuario {usuario.nombre}")
            print(f"DEBUG: Tipo solicitud: {tipo_solicitud_obj.nombre}")
            print(f"DEBUG: Estado: {estado_pendiente.nombre}")
            
            # Validar y guardar
            solicitud.full_clean()
            solicitud.save()
            
            print(f"DEBUG: Solicitud guardada con ID: {solicitud.id_solicitud}")
            
            messages.success(request, "Solicitud enviada correctamente.")
            return redirect("lista_solicitudes")
            
        except TipoSolicitud.DoesNotExist:
            messages.error(request, "El tipo de solicitud seleccionado no existe.")
            return render(request, "pages/solicitudes/form_solicitud.html", {
                "tipos_solicitud": tipos_solicitud,
                "data": {
                    "tipo_solicitud": tipo_id,
                    "dia_inicio": fecha_inicio,
                    "dia_fin": fecha_fin
                },
                "today": date.today()
            })
        except Exception as e:
            messages.error(request, f"Error al crear la solicitud: {str(e)}")
            print(f"ERROR: {str(e)}")
            return render(request, "pages/solicitudes/form_solicitud.html", {
                "tipos_solicitud": tipos_solicitud,
                "data": {
                    "tipo_solicitud": tipo_id,
                    "dia_inicio": fecha_inicio,
                    "dia_fin": fecha_fin
                },
                "today": date.today()
            })

    # GET request - mostrar formulario vacío
    return render(request, "pages/solicitudes/form_solicitud.html", {
        "tipos_solicitud": tipos_solicitud,
        "data": {},
        "today": date.today()
    })


def editar_solicitud(request: HttpRequest, id_solicitud: int) -> HttpResponse:
    """Editar una solicitud existente"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    solicitud = get_object_or_404(Solicitud, id_solicitud=id_solicitud)

    # Seguridad: solo quien creó la solicitud puede editarla
    if solicitud.id_usuario.id_usuario != usuario.id_usuario:
        messages.error(request, "No puedes editar esta solicitud.")
        return redirect("lista_solicitudes")

    # Solo se pueden editar solicitudes pendientes
    estado_pendiente = EstadoSolicitud.objects.get(nombre="Pendiente")
    if solicitud.estado_solicitud != estado_pendiente:
        messages.error(request, "Solo puedes editar solicitudes pendientes.")
        return redirect("lista_solicitudes")

    if request.method == "POST":
        tipo_id = request.POST.get("tipo_solicitud")
        fecha_inicio = request.POST.get("dia_inicio")
        fecha_fin = request.POST.get("dia_fin")

        if not tipo_id or not fecha_inicio or not fecha_fin:
            messages.error(request, "Todos los campos son obligatorios.")
        else:
            try:
                tipo_solicitud_obj = TipoSolicitud.objects.get(id_tipo=tipo_id)
                solicitud.tipo_solicitud = tipo_solicitud_obj
                solicitud.dia_inicio = fecha_inicio
                solicitud.dia_fin = fecha_fin
                
                # Validar los cambios
                solicitud.full_clean()
                solicitud.save()
                
                messages.success(request, "Solicitud actualizada correctamente.")
                return redirect("lista_solicitudes")
                
            except Exception as e:
                messages.error(request, f"Error al actualizar la solicitud: {str(e)}")

    tipos_solicitud = TipoSolicitud.objects.all()
    
    return render(request, "pages/solicitudes/editar_solicitud.html", {
        "solicitud": solicitud,
        "tipos_solicitud": tipos_solicitud,
        "today": date.today()
    })


def eliminar_solicitud(request: HttpRequest, id_solicitud: int) -> HttpResponse:
    """Eliminar una solicitud"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    solicitud = get_object_or_404(Solicitud, id_solicitud=id_solicitud)

    # Seguridad: solo quien creó la solicitud puede eliminarla
    if solicitud.id_usuario.id_usuario != usuario.id_usuario:
        messages.error(request, "No puedes eliminar esta solicitud.")
        return redirect("lista_solicitudes")

    # Solo se pueden eliminar solicitudes pendientes
    estado_pendiente = EstadoSolicitud.objects.get(nombre="Pendiente")
    if solicitud.estado_solicitud != estado_pendiente:
        messages.error(request, "Solo puedes eliminar solicitudes pendientes.")
        return redirect("lista_solicitudes")

    if request.method == "POST":
        try:
            solicitud.delete()
            messages.success(request, "Solicitud eliminada correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar la solicitud: {str(e)}")
        return redirect("lista_solicitudes")

    # GET → mostrar pantalla de confirmación
    return render(
        request,
        "pages/solicitudes/eliminar_solicitud.html",
        {"solicitud": solicitud}
    )
