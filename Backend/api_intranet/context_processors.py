# api_intranet/context_processors.py

from __future__ import annotations

from typing import Any, Optional

from .models import Usuario


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

