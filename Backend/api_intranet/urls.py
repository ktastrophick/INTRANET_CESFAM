from django.urls import path
from django.contrib.auth import views as auth_views
from .views import base_views, calendario_views, solicitudes_views, perfil_views, funcionarios_views

urlpatterns = [
    # Páginas base
    path('', base_views.inicio, name='inicio'),
    path('documentos/', base_views.documentos, name='documentos'),
    path('lista_funcionarios/', funcionarios_views.lista_funcionarios, name='lista_funcionarios'),
    path('form_funcionario/', funcionarios_views.form_funcionario, name='form_funcionario'),

    # Calendario (página y API CRUD)
    path('calendario/', calendario_views.calendario, name='calendario'),
    path('api/eventos/', calendario_views.eventos_api, name='eventos_api'),
    path('api/eventos/<int:id>/', calendario_views.evento_detalle_api, name='evento_api'),

    # Solicitudes
    path('solicitudes/', solicitudes_views.solicitudes, name='solicitudes'),
    path('form_solicitud/', solicitudes_views.form_solicitud, name='form_solicitud'),

    # Perfil
    path('perfil/', perfil_views.perfil, name='perfil'),

    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='pages/autenticacion.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

