"""
Vistas relacionadas con el perfil del usuario.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def perfil(request: HttpRequest) -> HttpResponse:
    """
    Vista del perfil del usuario autenticado.

    - Método soportado: GET.
    - Renderiza la plantilla 'pages/perfil.html'.
    - Envía en el contexto información básica del usuario si está autenticado.
    """
    context: dict[str, object] = {}

    if request.user.is_authenticated:
        # Puedes adaptar/expandir este contexto según tu modelo de usuario.
        context.update(
            {
                "usuario": request.user,
                # Ejemplos de claves que tu template podría usar:
                # "nombre_completo": request.user.get_full_name(),
                # "correo": request.user.email,
            }
        )

    return render(request, "pages/perfil.html", context)
