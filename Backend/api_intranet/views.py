from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from .models import Avisos, Calendario, Cargo, Departamento, EstadoSolicitud, InicioRegistrado 

def inicio(request):
    return render(request, 'pages/inicio.html')

#@login_required
def documentos(request):
    return render(request, 'pages/documentos.html')

#@login_required
def calendario(request):
    return render(request, 'pages/calendario.html')

#@login_required
def solicitudes(request):
    return render(request, 'pages/solicitudes.html')

#@login_required
def perfil(request):
    return render(request, 'pages/perfil.html')

