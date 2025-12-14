from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from api_intranet.models import Avisos
from api_intranet.models import get_usuario_actual
from django.utils import timezone


def crear_comunicado(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Método no permitido"})

    usuario = get_usuario_actual(request)
    if not usuario:
        return JsonResponse({"ok": False, "error": "No autenticado"})

    titulo = request.POST.get("titulo")
    descripcion = request.POST.get("descripcion")

    aviso = Avisos.objects.create(
        titulo=titulo,
        descripcion=descripcion,
        id_usuario=usuario,
        fecha_registro=timezone.now()
    )

    return JsonResponse({"ok": True, "id": aviso.id_aviso})


def listar_comunicados(request):
    avisos = Avisos.objects.select_related("id_usuario").order_by("-fecha_registro")

    return render(request, "pages/comunicados.html", {
        "avisos": avisos
    })
def listar_comunicados_json(request):
    avisos = Avisos.objects.select_related("id_usuario").order_by("-fecha_registro")

    data = [
        {
            "id": a.id_aviso,
            "titulo": a.titulo,
            "descripcion": a.descripcion,
            "usuario": a.id_usuario.nombre if a.id_usuario else "Desconocido",
            "fecha": timezone.localtime(a.fecha_registro).strftime("%d/%m/%Y %H:%M")
        }
        for a in avisos
    ]

    return JsonResponse(data, safe=False)
