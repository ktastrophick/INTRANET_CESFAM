from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def perfil(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/perfil.html')
