# api_intranet/views/autenticacion_views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista de inicio de sesión del usuario."""
    if request.method == "POST":
        usuario = request.POST.get("usuario")
        password = request.POST.get("password")

        user = authenticate(request, username=usuario, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Has iniciado sesión correctamente.")
            return redirect("inicio")  # Ajusta al nombre correcto

        messages.error(request, "Credenciales inválidas.")
        return render(request, "login.html")

    return render(request, "login.html")


def logout_view(request):
    """Cerrar sesión del usuario."""
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("login")
