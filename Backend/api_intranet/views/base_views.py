from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from api_intranet.models import Documento, Usuario

def inicio(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/inicio.html')

def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/index.html')




