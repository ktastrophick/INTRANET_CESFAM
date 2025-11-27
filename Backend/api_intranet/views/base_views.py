"""
Vistas base de la intranet (páginas generales como inicio e index).
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def inicio(request: HttpRequest) -> HttpResponse:
    """
    Vista de la página de inicio de la intranet.

    - Método soportado: GET.
    - Renderiza la plantilla 'pages/inicio.html'.
    """
    # En el futuro puedes agregar contexto adicional aquí, por ejemplo:
    # context = {"usuario": request.user}
    # return render(request, "pages/inicio.html", context)
    return render(request, "pages/inicio.html")


def index(request: HttpRequest) -> HttpResponse:
    """
    Vista de la página principal (dashboard) de la intranet.

    - Método soportado: GET.
    - Renderiza la plantilla 'pages/index.html'.
    """
    # Igual que en inicio, aquí puedes ir agregando datos agregados,
    # estadísticas u otra información para el dashboard.
    return render(request, "pages/index.html")
