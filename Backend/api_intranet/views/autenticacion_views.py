# api_intranet/views/autenticacion_views.py

from __future__ import annotations
from typing import Any

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

LOGIN_TEMPLATE: str = "autenticacion.html"  # tu template real


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    """
    Vista de inicio de sesión del usuario de la intranet.
    """
    context: dict[str, Any] = {}

    if request.method == "POST":
        usuario: str = (request.POST.get("usuario") or "").strip()
        password: str = request.POST.get("password") or ""

        if not usuario or not password:
            messages.error(request, "Debe ingresar usuario y contraseña.")
            context["usuario"] = usuario
            return render(request, LOGIN_TEMPLATE, context)

        if not usuario.isdigit():
            messages.error(
                request,
                "El usuario debe ser su RUT numérico sin puntos ni guion."
            )
            context["usuario"] = usuario
            return render(request, LOGIN_TEMPLATE, context)

        user = authenticate(request, username=usuario, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Has iniciado sesión correctamente.")
            # ⬇⬇⬇ AQUÍ EL CAMBIO IMPORTANTE
            return redirect("index")   # ya no 'inicio'

        messages.error(request, "Credenciales inválidas. Intente nuevamente.")
        context["usuario"] = usuario
        return render(request, LOGIN_TEMPLATE, context)

    return render(request, LOGIN_TEMPLATE, context)


@require_http_methods(["GET"])
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("login")
