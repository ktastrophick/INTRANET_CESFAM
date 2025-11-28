# api_intranet/urls.py - VERSIÓN CORREGIDA
from django.urls import path
from django.contrib.auth import views as auth_views

# Importaciones específicas para evitar confusiones
from .views.base_views import inicio, index, login_personalizado, logout_personalizado
from .views.calendario_views import calendario, eventos_api, evento_detalle_api
from .views.solicitudes_views import (lista_solicitudes, form_solicitud, editar_solicitud, 
                                    eliminar_solicitud, aprobar_jefe, rechazar_jefe, 
                                    aprobar_director, rechazar_director, descargar_solicitud)
from .views.perfil_views import perfil, editar_perfil, cambiar_contrasena
from .views.funcionarios_views import (lista_funcionarios, form_funcionario, 
                                        editar_funcionario, eliminar_funcionario)
from .views.documentos_views import (lista_documentos, form_documento, 
                                    editar_documento, eliminar_documento)
from .views.licencias_views import (lista_licencias, form_licencia, editar_licencia, 
                                    eliminar_licencia, detalle_licencia)

urlpatterns = [
    # =============================================
    # PÁGINAS BASE
    # =============================================
    path('', inicio, name='inicio'),    
    path('index/', index, name='index'),

    # =============================================
    # CALENDARIO - IMPORTACIONES DIRECTAS
    # =============================================
    path('calendario/', calendario, name='calendario'),
    path('api/eventos/', eventos_api, name='eventos_api'),
    path('api/eventos/<int:id>/', evento_detalle_api, name='evento_api'),

    # =============================================
    # DOCUMENTOS
    # =============================================
    path('documentos/', lista_documentos, name='lista_documentos'),
    path('form_documento/', form_documento, name='form_documento'),
    path('documentos/editar/<int:id_documento>/', editar_documento, name='editar_documento'),
    path('documentos/eliminar/<int:id_documento>/', eliminar_documento, name='eliminar_documento'),

    # =============================================
    # FUNCIONARIOS
    # =============================================
    path('funcionarios/', lista_funcionarios, name='lista_funcionarios'),
    path('form_funcionario/', form_funcionario, name='form_funcionario'),
    path('funcionarios/editar/<int:id_usuario>/', editar_funcionario, name='editar_funcionario'),
    path('funcionarios/eliminar/<int:id_usuario>/', eliminar_funcionario, name='eliminar_funcionario'),

    # =============================================
    # SOLICITUDES
    # =============================================
    path('solicitudes/', lista_solicitudes, name='lista_solicitudes'),
    path('form_solicitud/', form_solicitud, name='form_solicitud'),
    path('solicitudes/editar/<int:id_solicitud>/', editar_solicitud, name='editar_solicitud'),
    path('solicitudes/eliminar/<int:id_solicitud>/', eliminar_solicitud, name='eliminar_solicitud'),
    
    # Aprobaciones de solicitudes
    path('solicitudes/aprobar-jefe/<int:id_solicitud>/', aprobar_jefe, name='aprobar_jefe'),
    path('solicitudes/rechazar-jefe/<int:id_solicitud>/', rechazar_jefe, name='rechazar_jefe'),
    path('solicitudes/aprobar-director/<int:id_solicitud>/', aprobar_director, name='aprobar_director'),
    path('solicitudes/rechazar-director/<int:id_solicitud>/', rechazar_director, name='rechazar_director'),
    path('solicitud/<int:id_solicitud>/descargar/', descargar_solicitud, name='descargar_solicitud'),

    # =============================================
    # PERFIL DE USUARIO
    # =============================================
    path('perfil/', perfil, name='perfil'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),
    path('perfil/cambiar-contrasena/', cambiar_contrasena, name='cambiar_contrasena'),

    # =============================================
    # LICENCIAS MÉDICAS
    # =============================================
    path('licencias/', lista_licencias, name='lista_licencias'),
    path('form_licencia/', form_licencia, name='form_licencia'),
    path('licencias/editar/<int:id_licencia>/', editar_licencia, name='editar_licencia'),
    path('licencias/eliminar/<int:id_licencia>/', eliminar_licencia, name='eliminar_licencia'),
    path('licencias/detalle/<int:id_licencia>/', detalle_licencia, name='detalle_licencia'),

    # =============================================
    # AUTENTICACIÓN
    # =============================================
    path('login/', login_personalizado, name='login'),
    path('logout/', logout_personalizado, name='logout'),
]