# api_intranet/context_processors.py

from __future__ import annotations

from typing import Any, Optional
from django.conf import settings

from .models import Usuario, Perfil


def rol_usuario(request):
    """
    Inyecta en el contexto:
        - rol_usuario: tomado directamente de la sesión
        - usuario_sistema: opcional (si quieres mantenerlo)
    """
    usuario_sistema = None
    rol = request.session.get("usuario_rol")  # <-- AQUÍ está el rol correcto

    return {
        "usuario_sistema": usuario_sistema,
        "rol_usuario": rol,  # <-- esto usarás en los templates
    }


def perfil_usuario(request):
    """
    Context processor para hacer disponible la foto de perfil
    del usuario en todas las plantillas.
    
    Inyecta en el contexto:
        - perfil_foto: URL de la foto de perfil (si existe)
        - perfil_obj: objeto Perfil completo (si existe)
    """
    context = {
        'perfil_foto': None,
        'perfil_obj': None,
    }
    
    # Verificar si hay un usuario en sesión
    user_id = request.session.get('id_usuario')
    
    if user_id:
        try:
            usuario = Usuario.objects.get(id_usuario=user_id)
            
            # Intentar obtener el perfil del usuario
            try:
                perfil = Perfil.objects.get(id_usuario=usuario)
                context['perfil_obj'] = perfil
                
                # Construir la URL de la foto
                if perfil.foto_perfil:
                    # Si usas ImageField
                    if hasattr(perfil.foto_perfil, 'url'):
                        context['perfil_foto'] = perfil.foto_perfil.url
                    # Si usas CharField (solución temporal)
                    else:
                        context['perfil_foto'] = f"{settings.MEDIA_URL}{perfil.foto_perfil}"
                        
            except Perfil.DoesNotExist:
                # Si no existe el perfil, no hay foto
                pass
                
        except Usuario.DoesNotExist:
            # Usuario no existe
            pass
    
    return context