from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from api_intranet.models import Documento, Usuario
from django.contrib.auth.decorators import login_required
from typing import Optional

def get_usuario_actual(request: HttpRequest) -> Optional[Usuario]:
    """Obtiene el usuario actual desde la sesión"""
    user_id = request.session.get("id_usuario")
    if not user_id:
        return None
    try:
        return Usuario.objects.get(id_usuario=user_id)
    except Usuario.DoesNotExist:
        return None


def lista_documentos(request: HttpRequest) -> HttpResponse:
    """Lista todos los documentos del sistema"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    documentos = Documento.objects.select_related('subido_por').all().order_by('-fecha_subida')
    
    # Filtrar por búsqueda si se proporciona
    query = request.GET.get('q')
    if query:
        documentos = documentos.filter(nombre__icontains=query)
    
    context = {
        "documentos": documentos,
        "usuario": usuario,
        "query": query
    }
    return render(request, "pages/documentos/lista_documentos.html", context)


def form_documento(request: HttpRequest) -> HttpResponse:
    """Formulario para subir nuevo documento"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        archivo = request.FILES.get("archivo")

        # Validaciones
        if not nombre:
            messages.error(request, "El nombre del documento es obligatorio.")
            return render(request, "pages/documentos/form_documento.html", {
                "data": {
                    "nombre": nombre,
                    "descripcion": descripcion
                }
            })

        if not archivo:
            messages.error(request, "Debes seleccionar un archivo para subir.")
            return render(request, "pages/documentos/form_documento.html", {
                "data": {
                    "nombre": nombre,
                    "descripcion": descripcion
                }
            })

        try:
            # Crear el documento con validaciones del modelo
            documento = Documento(
                nombre=nombre,
                descripcion=descripcion or None,
                archivo=archivo,
                subido_por=usuario
            )
            
            # Aplicar validaciones del modelo
            documento.full_clean()
            documento.save()
            
            messages.success(request, f"Documento '{nombre}' subido exitosamente.")
            return redirect("lista_documentos")
            
        except Exception as e:
            messages.error(request, f"Error al subir el documento: {str(e)}")
            return render(request, "pages/documentos/form_documento.html", {
                "data": {
                    "nombre": nombre,
                    "descripcion": descripcion
                }
            })

    # GET request - mostrar formulario vacío
    return render(request, "pages/documentos/form_documento.html")


def editar_documento(request: HttpRequest, id_documento: int) -> HttpResponse:
    """Editar documento existente"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    documento = get_object_or_404(Documento, id_documento=id_documento)

    # Verificar permisos: solo el que subió el documento o admin puede editarlo
    if documento.subido_por.id_usuario != usuario.id_usuario and not (usuario.id_rol and usuario.id_rol.nombre == 'Admin'):
        messages.error(request, "No tienes permisos para editar este documento.")
        return redirect("lista_documentos")

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        archivo = request.FILES.get("archivo")

        if not nombre:
            messages.error(request, "El nombre del documento es obligatorio.")
            return render(request, "pages/documentos/editar_documento.html", {
                "documento": documento
            })

        try:
            documento.nombre = nombre
            documento.descripcion = descripcion or None
            
            # Actualizar archivo si se proporciona uno nuevo
            if archivo:
                documento.archivo = archivo
            
            # Aplicar validaciones del modelo
            documento.full_clean()
            documento.save()
            
            messages.success(request, f"Documento '{nombre}' actualizado exitosamente.")
            return redirect("lista_documentos")
            
        except Exception as e:
            messages.error(request, f"Error al actualizar el documento: {str(e)}")
            return render(request, "pages/documentos/editar_documento.html", {
                "documento": documento
            })

    # GET request - mostrar formulario con datos actuales
    return render(request, "pages/documentos/editar_documento.html", {
        "documento": documento
    })


def eliminar_documento(request: HttpRequest, id_documento: int) -> HttpResponse:
    """Eliminar documento"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    documento = get_object_or_404(Documento, id_documento=id_documento)

    # Verificar permisos: solo el que subió el documento o admin puede eliminarlo
    if documento.subido_por.id_usuario != usuario.id_usuario and not (usuario.id_rol and usuario.id_rol.nombre == 'Admin'):
        messages.error(request, "No tienes permisos para eliminar este documento.")
        return redirect("lista_documentos")

    if request.method == "POST":
        try:
            nombre_documento = documento.nombre
            documento.delete()
            messages.success(request, f"Documento '{nombre_documento}' eliminado exitosamente.")
            return redirect("lista_documentos")
        except Exception as e:
            messages.error(request, f"Error al eliminar el documento: {str(e)}")
            return redirect("lista_documentos")

    # GET request - mostrar confirmación
    return render(request, "pages/documentos/eliminar_documento.html", {
        "documento": documento
    })