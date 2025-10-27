from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from api_intranet.models import Usuario

def inicio(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/inicio.html')

def documentos(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/documentos.html')
