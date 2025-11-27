"""
Vistas base de la intranet (páginas generales como inicio e index).
"""

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse


def inicio(request: HttpRequest) -> HttpResponse:
    """
    Vista de la página pública de inicio.

    - Si el usuario NO está autenticado → muestra la portada (landing).
    - Si el usuario está autenticado → redirige al dashboard (index).

    Plantilla: 'pages/inicio.html'
    """
    if request.user.is_authenticated:
        return redirect("index")

    return render(request, "pages/inicio.html")


def index(request: HttpRequest) -> HttpResponse:
    """
    Vista del dashboard principal.

    - Solo accesible si el usuario está autenticado.
    - Si no lo está → redirige al login.

    Plantilla: 'pages/index.html'
    """
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "pages/index.html")

