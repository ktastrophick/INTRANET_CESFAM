from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def solicitudes(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/solicitudes.html')

def form_solicitud(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/form_solicitud.html')
