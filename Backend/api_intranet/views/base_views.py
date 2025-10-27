from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from api_intranet.models import Documento, Usuario

def inicio(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/inicio.html')

def documentos(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/documentos.html')

def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/index.html')

def form_documento(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/form_documento.html')


