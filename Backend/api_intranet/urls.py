from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (base_views, calendario_views, solicitudes_views, perfil_views, funcionarios_views, 
                    documentos_views, licencias_views, autenticacion_views)

urlpatterns = [
    # Páginas base
    path('', base_views.inicio, name='inicio'),    
    path('index/', base_views.index, name='index'),

    #Documentos
    path('documentos/', documentos_views.lista_documentos, name='lista_documentos'),
    path('form_documento/', documentos_views.form_documento, name='form_documento'),
    path('documentos/editar/<int:id_documento>/', documentos_views.editar_documento, name='editar_documento'),
    path('documentos/eliminar/<int:id_documento>/', documentos_views.eliminar_documento, name='eliminar_documento'),

    #Funcionarios
    path('funcionarios/', funcionarios_views.lista_funcionarios, name='lista_funcionarios'),
    path('form_funcionario/', funcionarios_views.form_funcionario, name='form_funcionario'),
    path('funcionarios/editar/<int:id_usuario>/', funcionarios_views.editar_funcionario, name='editar_funcionario'),
    path('funcionarios/eliminar/<int:id_usuario>/', funcionarios_views.eliminar_funcionario, name='eliminar_funcionario'),

    # Calendario (página y API CRUD)
    path('calendario/', calendario_views.calendario, name='calendario'),
    path('api/eventos/', calendario_views.eventos_api, name='eventos_api'),
    path('api/eventos/<int:id>/', calendario_views.evento_detalle_api, name='evento_api'),

    # Solicitudes
    path('solicitudes/', solicitudes_views.lista_solicitudes, name='lista_solicitudes'),
    path('form_solicitud/', solicitudes_views.form_solicitud, name='form_solicitud'),
    path('solicitudes/editar/<int:id_solicitud>/', solicitudes_views.editar_solicitud, name='editar_solicitud'),
    path('solicitudes/eliminar/<int:id_solicitud>/', solicitudes_views.eliminar_solicitud, name='eliminar_solicitud'),

    # Perfil
    path('perfil/', perfil_views.perfil, name='perfil'),

    #Licencias
    path('licencias/', licencias_views.lista_licencias, name='lista_licencias'),
    path('form_licencia/', licencias_views.form_licencia, name='form_licencia'),
    path('licencias/editar/<int:id_licencia>/', licencias_views.editar_licencia, name='editar_licencia'),
    path('licencias/eliminar/<int:id_licencia>/', licencias_views.eliminar_licencia, name='eliminar_licencia'),

    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='pages/autenticacion.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
]

