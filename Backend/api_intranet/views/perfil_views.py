from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def perfil(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/perfil.html')

from django.shortcuts import render

def licencias(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/licencias.html')

def form_licencia(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/form_licencia.html')