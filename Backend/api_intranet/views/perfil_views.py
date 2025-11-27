"""
Vistas relacionadas con el perfil del usuario.
"""

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from api_intranet.models import Usuario, Perfil
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


def cambiar_contrasena(request: HttpRequest) -> HttpResponse:
    """
    Vista para cambiar la contraseña del usuario.
    
    - Métodos soportados: GET, POST
    """
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    if request.method == "POST":
        contrasena_actual = request.POST.get("contrasena_actual", "").strip()
        nueva_contrasena = request.POST.get("nueva_contrasena", "").strip()
        confirmar_contrasena = request.POST.get("confirmar_contrasena", "").strip()

        # Validaciones
        if not all([contrasena_actual, nueva_contrasena, confirmar_contrasena]):
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, "pages/cambiar_contrasena.html")

        # Verificar contraseña actual (esto depende de cómo manejes las contraseñas)
        if usuario.contrasena != contrasena_actual:  # Ajusta según tu sistema de autenticación
            messages.error(request, "La contraseña actual es incorrecta.")
            return render(request, "pages/cambiar_contrasena.html")

        if nueva_contrasena != confirmar_contrasena:
            messages.error(request, "Las nuevas contraseñas no coinciden.")
            return render(request, "pages/cambiar_contrasena.html")

        if len(nueva_contrasena) < 6:
            messages.error(request, "La nueva contraseña debe tener al menos 6 caracteres.")
            return render(request, "pages/cambiar_contrasena.html")

        try:
            # Actualizar contraseña
            usuario.contrasena = nueva_contrasena
            usuario.full_clean()
            usuario.save()
            
            messages.success(request, "Contraseña cambiada exitosamente.")
            return redirect("perfil")
            
        except Exception as e:
            messages.error(request, f"Error al cambiar la contraseña: {str(e)}")

    return render(request, "pages/cambiar_contrasena.html")