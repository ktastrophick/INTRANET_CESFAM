# api_intranet/views/autenticacion_views.py

from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods


LOGIN_TEMPLATE: str = "login.html"


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    """
    Vista de inicio de sesión del usuario.

    - GET: muestra el formulario de login.
    - POST: procesa las credenciales enviadas y autentica al usuario.
    """
    context: dict[str, Any] = {}

    if request.method == "POST":
        usuario: str = (request.POST.get("usuario") or "").strip()
        password: str = request.POST.get("password") or ""

        # Validaciones básicas de campos vacíos
        if not usuario or not password:
            messages.error(request, "Debe ingresar usuario y contraseña.")
            context["usuario"] = usuario  # Para rellenar el campo usuario de vuelta
            return render(request, LOGIN_TEMPLATE, context)

        user = authenticate(request, username=usuario, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Has iniciado sesión correctamente.")
            # No se cambia el nombre de la URL, se asume que 'inicio' existe en urls.py
            return redirect("inicio")

        # Si la autenticación falla
        messages.error(request, "Credenciales inválidas. Intente nuevamente.")
        context["usuario"] = usuario
        return render(request, LOGIN_TEMPLATE, context)

    # Método GET: simplemente se muestra el formulario
    return render(request, LOGIN_TEMPLATE, context)


@require_http_methods(["GET"])
def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Cerrar sesión del usuario.

    - GET: cierra la sesión actual y redirige a la página de login.
    """
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    # Se asume que 'login' es el nombre de la URL del formulario de inicio de sesión
    return redirect("login")

