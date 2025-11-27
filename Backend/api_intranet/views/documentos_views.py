from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from api_intranet.models import Documento

def lista_documentos(request):
    documentos = Documento.objects.select_related('subido_por').all().order_by('-fecha_subida')
    return render(request, "pages/documentos/lista_documentos.html", {
        "documentos": documentos
    })

def form_documento(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        archivo = request.FILES.get("archivo")

        # Validación simple opcional
        if not archivo:
            return render(request, "pages/documentos/form_documento.html", {
                "error": "Debes subir un archivo."
            })

        # Guardar en la base de datos
        Documento.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            archivo=archivo,
            subido_por=request.user  # o el usuario que corresponda
        )

        return redirect("documentos_lista")  # redirige de vuelta a la tabla

    return render(request, "pages/documentos/form_documento.html")

def editar_documento(request, id_documento):
    documento = get_object_or_404(Documento, id_documento=id_documento)

    return render(request, "pages/documentos/editar_documento.html", {
        "documento": documento
    })

def eliminar_documento(request, id_documento):
    documento = get_object_or_404(Documento, id_documento=id_documento)

    if request.method == "POST":
        documento.delete()
        return redirect("documentos")  # Ajusta si tu URL tiene otro nombre

    return render(request, "pages/documentos/eliminar_documento.html", {
        "documento": documento
    })
