from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from api_intranet.models import Licencia, Usuario
from django.utils import timezone

def lista_licencias(request):
    licencias = Licencia.objects.select_related("id_usuario").all().order_by('-fecha_registro')
    return render(request, "pages/licencias/lista_licencias.html", {"licencias": licencias})

def form_licencia(request):
    if request.method == "POST":
        dia_inicio = request.POST.get("dia_inicio")
        dia_fin = request.POST.get("dia_fin")
        imagen = request.FILES.get("imagen")

        # ⚠️ Ajusta esto según tu sistema de login
        usuario = Usuario.objects.first()  # o request.user si usas auth

        Licencia.objects.create(
            dia_inicio=dia_inicio,
            dia_fin=dia_fin,
            imagen=imagen,
            id_usuario=usuario,
            fecha_registro=timezone.now()
        )

        return redirect("lista_licencias")  

    return render(request, "pages/licencias/form_licencia.html")

def editar_licencia(request, id_licencia):
    licencia = get_object_or_404(Licencia, id_licencia=id_licencia)

    if request.method == "POST":
        licencia.dia_inicio = request.POST.get("dia_inicio")
        licencia.dia_fin = request.POST.get("dia_fin")

        if request.FILES.get("imagen"):
            licencia.imagen = request.FILES.get("imagen")

        licencia.save()
        return redirect("lista_licencias")

    return render(request, "pages/licencias/editar_licencia.html", {"licencia": licencia})

def eliminar_licencia(request, id_licencia):
    licencia = get_object_or_404(Licencia, id_licencia=id_licencia)

    if request.method == "POST":
        licencia.delete()
        return redirect("lista_licencias")

    return render(request, "pages/licencias/confirmar_eliminar.html", {"licencia": licencia})

