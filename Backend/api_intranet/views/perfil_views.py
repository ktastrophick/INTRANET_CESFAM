"""
Vistas relacionadas con el perfil del usuario.
"""

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from api_intranet.models import Usuario, Perfil
from django.core.files.storage import default_storage
from typing import Optional
import os


def get_usuario_actual(request: HttpRequest) -> Optional[Usuario]:
    """Obtiene el usuario actual desde la sesión"""
    user_id = request.session.get("id_usuario")
    if not user_id:
        return None
    try:
        return Usuario.objects.get(id_usuario=user_id)
    except Usuario.DoesNotExist:
        return None


def perfil(request: HttpRequest) -> HttpResponse:
    """
    Vista del perfil del usuario autenticado.

    - Método soportado: GET.
    - Renderiza la plantilla 'pages/perfil.html'.
    - Envía en el contexto información completa del usuario desde el modelo Usuario.
    """
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    # Obtener o crear el perfil extendido del usuario
    perfil_obj, created = Perfil.objects.get_or_create(id_usuario=usuario)
    

    context = {
        "usuario": usuario,
        "perfil": perfil_obj,
        "rol": usuario.id_rol.nombre if usuario.id_rol else "Sin rol",
        "departamento": usuario.id_departamento.nombre if usuario.id_departamento else "Sin departamento",
        "cargo": usuario.id_cargo.nombre if usuario.id_cargo else "Sin cargo",
    }

    return render(request, "pages/perfil.html", context)


def editar_perfil(request: HttpRequest) -> HttpResponse:
    """
    Vista para editar el perfil del usuario.
    
    - Métodos soportados: GET, POST
    - Permite actualizar información básica del perfil
    """
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    perfil_obj, created = Perfil.objects.get_or_create(id_usuario=usuario)

    if request.method == "POST":
        # Actualizar información del perfil extendido
        nueva_descripcion = request.POST.get("descripcion", "").strip()
        
        # Manejar foto de perfil si se sube
        foto_perfil = request.FILES.get("foto_perfil")
        
        try:
            # Actualizar campos del perfil
            if nueva_descripcion:
                perfil_obj.descripcion = nueva_descripcion
            
            if foto_perfil:
                perfil_obj.foto_perfil = foto_perfil
            
            # Aplicar validaciones
            perfil_obj.full_clean()
            perfil_obj.save()
            
            messages.success(request, "Perfil actualizado exitosamente.")
            return redirect("perfil")
            
        except Exception as e:
            messages.error(request, f"Error al actualizar el perfil: {str(e)}")

    context = {
        "usuario": usuario,
        "perfil": perfil_obj,
    }

    return render(request, "pages/editar_perfil.html", context)


def actualizar_foto_perfil(request: HttpRequest) -> HttpResponse:
    """
    Vista para actualizar solo la foto de perfil del usuario.
    
    - Método soportado: POST
    - Valida el tipo y tamaño del archivo
    - Elimina la foto anterior si existe
    - Guarda la nueva foto
    """
    if request.method != 'POST':
        return redirect('perfil')
    
    # Verificar que el usuario esté autenticado
    user_id = request.session.get('id_usuario')
    if not user_id:
        messages.error(request, 'Debes iniciar sesión para actualizar tu foto de perfil')
        return redirect('login')
    
    try:
        # Obtener el usuario
        usuario = Usuario.objects.get(id_usuario=user_id)
        
        # Obtener o crear el perfil
        perfil_obj, created = Perfil.objects.get_or_create(id_usuario=usuario)
        
        # Obtener el archivo de imagen
        foto = request.FILES.get('foto_perfil')
        
        if not foto:
            messages.error(request, 'No se seleccionó ninguna imagen')
            return redirect('perfil')
        
        # Verificar que la foto tenga el atributo size
        if not hasattr(foto, 'size') or foto.size is None:
            messages.error(request, 'El archivo de imagen no es válido')
            return redirect('perfil')
        
        # Validar el tamaño del archivo (5MB máximo)
        max_size = 5 * 1024 * 1024  # 5MB en bytes
        if foto.size > max_size:
            messages.error(request, f'La imagen no puede superar {max_size // (1024*1024)}MB')
            return redirect('perfil')
        
        # Validar que el tamaño no sea 0
        if foto.size == 0:
            messages.error(request, 'El archivo de imagen está vacío')
            return redirect('perfil')
        
        # Validar el tipo de archivo
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        file_type_valid = False
        
        # Verificar content_type primero
        if foto.content_type and foto.content_type in allowed_types:
            file_type_valid = True
        else:
            # Como fallback, verificar la extensión del archivo si tiene nombre
            if foto.name:
                file_name = foto.name.lower()
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                for ext in allowed_extensions:
                    if file_name.endswith(ext):
                        file_type_valid = True
                        break
        
        if not file_type_valid:
            messages.error(request, 'Solo se permiten imágenes JPG, PNG o GIF')
            return redirect('perfil')
        
        # Si existe una foto anterior, eliminarla
        if perfil_obj.foto_perfil:
            try:
                # Verificar si el archivo existe antes de intentar eliminarlo
                if perfil_obj.foto_perfil.name and default_storage.exists(perfil_obj.foto_perfil.name):
                    default_storage.delete(perfil_obj.foto_perfil.name)
            except Exception as e:
                print(f"Error al eliminar foto anterior: {e}")
                # Continuar de todos modos para guardar la nueva foto
        
        # Guardar la nueva foto
        perfil_obj.foto_perfil = foto
        perfil_obj.save()
        
        messages.success(request, 'Foto de perfil actualizada correctamente')
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Error al actualizar la foto de perfil: {str(e)}')
        print(f"Error en actualizar_foto_perfil: {e}")
    
    return redirect('perfil')