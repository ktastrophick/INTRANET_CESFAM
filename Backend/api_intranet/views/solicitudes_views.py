from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from api_intranet.models import Solicitud, TipoSolicitud, EstadoSolicitud, Usuario
from django.utils import timezone

'''def lista_solicitudes(request):
    usuario = request.session["usuario"]
    rol = usuario.id_rol.id_rol   # 1=Director, 3=Jefe, 4=Funcionario

    if rol == 4:  # Funcionario
        solicitudes = Solicitud.objects.filter(id_usuario=usuario)

    elif rol == 3:  # Jefe de depto
        solicitudes = Solicitud.objects.filter(
            id_usuario__id_departamento=usuario.id_departamento
        )

    elif rol == 1:  # Director
        solicitudes = Solicitud.objects.filter(
            aprobacion_jefe=True,
            aprobacion_director__isnull=True
        )

    return render(request, "pages/solicitudes/lista_solicitudes.html", {"solicitudes": solicitudes})'''

def lista_solicitudes(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/solicitudes/lista_solicitudes.html')

def aprobar_jefe(request, id_solicitud):
    solicitud = Solicitud.objects.get(id_solicitud=id_solicitud)

    if solicitud.aprobacion_jefe is not None:
        messages.error(request, "Ya fue revisada por el jefe.")
        return redirect("lista_solicitudes")

    solicitud.aprobacion_jefe = True
    solicitud.save()
    messages.success(request, "Solicitud aprobada y enviada al Director.")
    return redirect("lista_solicitudes")


def rechazar_jefe(request, id_solicitud):
    solicitud = Solicitud.objects.get(id_solicitud=id_solicitud)

    if solicitud.aprobacion_jefe is not None:
        messages.error(request, "Ya fue revisada por el jefe.")
        return redirect("lista_solicitudes")

    solicitud.aprobacion_jefe = False
    solicitud.estado_solicitud_id = 3  # Rechazado (configúralo)
    solicitud.save()
    messages.success(request, "Solicitud rechazada.")
    return redirect("lista_solicitudes")

def aprobar_director(request, id_solicitud):
    solicitud = Solicitud.objects.get(id_solicitud=id_solicitud)

    if solicitud.aprobacion_director is not None:
        messages.error(request, "Ya fue revisada por el director.")
        return redirect("lista_solicitudes")

    solicitud.aprobacion_director = True

    # si jefe aprobó y director aprobó → estado final aprobado
    if solicitud.aprobacion_jefe and solicitud.aprobacion_director:
        solicitud.estado_solicitud_id = 2  # Aprobado (coloca id correcto)

    solicitud.save()
    messages.success(request, "Solicitud aprobada completamente.")
    return redirect("lista_solicitudes")


def rechazar_director(request, id_solicitud):
    solicitud = Solicitud.objects.get(id_solicitud=id_solicitud)

    if solicitud.aprobacion_director is not None:
        messages.error(request, "Ya fue revisada por el director.")
        return redirect("lista_solicitudes")

    solicitud.aprobacion_director = False
    solicitud.estado_solicitud_id = 3  # Rechazado
    solicitud.save()

    messages.success(request, "Solicitud rechazada por el Director.")
    return redirect("lista_solicitudes")


def form_solicitud(request):
    if request.method == "POST":
        tipo_id = request.POST.get("tipo_solicitud")
        fecha_inicio = request.POST.get("dia_inicio")
        fecha_fin = request.POST.get("dia_fin")
        motivo = request.POST.get("motivo", "")

        if not fecha_inicio or not fecha_fin:
            messages.error(request, "Debe seleccionar un rango de fechas.")
            return redirect("solicitudes")

        solicitud = Solicitud.objects.create(
            dia_inicio=fecha_inicio,
            dia_fin=fecha_fin,
            tipo_solicitud_id=tipo_id,
            id_usuario=request.user,   # Asumiendo que request.user es tu Usuario
            estado_solicitud_id=1,     # Pendiente
            fecha_registro=timezone.now(),
        )

        messages.success(request, "Solicitud enviada correctamente.")
        return redirect("solicitudes")

    # Si es GET
    tipos_solicitud = TipoSolicitud.objects.all()
    return render(request, "pages/solicitudes/form_solicitud.html", {
        "tipos_solicitud": tipos_solicitud
    })

def editar_solicitud(request, id_solicitud):
    solicitud = get_object_or_404(Solicitud, id_solicitud=id_solicitud)

    # seguridad: solo quien creó la solicitud puede editarla
    usuario = request.session["usuario"]
    if solicitud.id_usuario.id_usuario != usuario.id_usuario:
        messages.error(request, "No puedes editar esta solicitud.")
        return redirect("lista_solicitudes")

    if solicitud.estado_solicitud_id != 1:  # 1 = Pendiente
        messages.error(request, "Solo puedes editar solicitudes pendientes.")
        return redirect("lista_solicitudes")

    if request.method == "POST":
        solicitud.tipo_solicitud_id = request.POST.get("tipo_solicitud")
        solicitud.dia_inicio = request.POST.get("dia_inicio")
        solicitud.dia_fin = request.POST.get("dia_fin")
        solicitud.save()

        messages.success(request, "Solicitud actualizada correctamente.")
        return redirect("lista_solicitudes")

    tipos = TipoSolicitud.objects.all()

    return render(request, "pages/solicitudes/editar_solicitud.html", {
        "solicitud": solicitud,
        "tipos_solicitud": tipos,
    })

def eliminar_solicitud(request, id_solicitud):
    solicitud = get_object_or_404(Solicitud, id_solicitud=id_solicitud)

    usuario = request.session["usuario"]
    if solicitud.id_usuario.id_usuario != usuario.id_usuario:
        messages.error(request, "No puedes eliminar esta solicitud.")
        return redirect("lista_solicitudes")

    if solicitud.estado_solicitud_id != 1:  # Solo pendientes
        messages.error(request, "Solo puedes eliminar solicitudes pendientes.")
        return redirect("lista_solicitudes")

    solicitud.delete()
    messages.success(request, "Solicitud eliminada correctamente.")

    return redirect("lista_solicitudes")
