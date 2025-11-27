# api_intranet/context_processors.py

from __future__ import annotations

from typing import Any, Optional

from .models import Usuario


def rol_usuario(request) -> dict[str, Any]:
    """
    Inyecta en el contexto:
      - usuario_sistema: instancia de Usuario (si se encuentra por RUT)
      - rol_usuario: rol asociado (si existe en el modelo)

    Regla:
      - Si el username es numérico, se asume que es el RUT (sin DV).
      - Si el username NO es numérico (ej: 'admincesfam'), no se vincula
        con Usuario y no se lanza ningún error.
    """
    usuario_sistema: Optional[Usuario] = None
    rol_usuario: Any = None

    if request.user.is_authenticated:
        username = request.user.username

        # Solo intentamos usarlo como RUT si es numérico
        if username.isdigit():
            rut_int = int(username)

            usuario_sistema = (
                Usuario.objects
                .filter(rut=rut_int)
                .first()
            )

            if usuario_sistema is not None:
                # Ajusta según cómo tengas el rol en el modelo
                rol_usuario = getattr(usuario_sistema, "rol", None)
                if rol_usuario is None:
                    rol_usuario = getattr(usuario_sistema, "rol_usuario", None)

    return {
        "usuario_sistema": usuario_sistema,
        "rol_usuario": rol_usuario,
    }
