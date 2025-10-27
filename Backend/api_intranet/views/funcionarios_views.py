from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from api_intranet.models import Usuario
def lista_funcionarios(request: HttpRequest) -> HttpResponse:
    # Obtener filtro por inicial desde GET
    inicial = request.GET.get("inicial")
    
    if inicial:
        funcionarios = Usuario.objects.filter(nombre__istartswith=inicial)
    else:
        funcionarios = Usuario.objects.all()
    
    return render(
        request,
        'pages/lista_funcionarios.html',
        {'funcionarios': funcionarios}
    )
def form_funcionario(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/form_funcionario.html')