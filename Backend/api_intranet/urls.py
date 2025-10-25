from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('documentos/', views.documentos, name='documentos'),
    path('calendario/', views.calendario, name='calendario'),
    path('solicitudes/', views.solicitudes, name='solicitudes'),
    path('perfil/', views.perfil, name='perfil'),
]


