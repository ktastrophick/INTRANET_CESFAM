from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (base_views, calendario_views, solicitudes_views, perfil_views, funcionarios_views, 
                    documentos_views, licencias_views, comunicado_views)

urlpatterns = [



    path('', base_views.inicio, name='inicio'),    
    path('index/', base_views.index, name='index'),


    # =============================================
    # DOCUMENTOS
    # =============================================
    path('documentos/', documentos_views.lista_documentos, name='lista_documentos'),
    path('form_documento/', documentos_views.form_documento, name='form_documento'),
    path('documentos/editar/<int:id_documento>/', documentos_views.editar_documento, name='editar_documento'),
    path('documentos/eliminar/<int:id_documento>/', documentos_views.eliminar_documento, name='eliminar_documento'),

    # =============================================
    # FUNCIONARIOS
    # =============================================
    path('funcionarios/', funcionarios_views.lista_funcionarios, name='lista_funcionarios'),
    path('form_funcionario/', funcionarios_views.form_funcionario, name='form_funcionario'),
    path('funcionarios/editar/<int:id_usuario>/', funcionarios_views.editar_funcionario, name='editar_funcionario'),
    path('funcionarios/eliminar/<int:id_usuario>/', funcionarios_views.eliminar_funcionario, name='eliminar_funcionario'),

    # =============================================
    # CALENDARIO
    # =============================================
    path('calendario/', calendario_views.calendario, name='calendario'),
    path('api/eventos/', calendario_views.eventos_api, name='eventos_api'),
    path('api/eventos/<int:id>/', calendario_views.evento_detalle_api, name='evento_api'),

    path("comunicados/", comunicado_views.listar_comunicados, name="comunicados"),
    path("comunicados/crear/", comunicado_views.crear_comunicado, name="crear_comunicado"),
    path("comunicados/listar/", comunicado_views.listar_comunicados_json, name="comunicados_listar"),
    path("comunicados/editar/<int:id_aviso>/", comunicado_views.editar_comunicado),
    path("comunicados/eliminar/<int:id_aviso>/", comunicado_views.eliminar_comunicado),

    path("calendario/tipos/",calendario_views.tipos_evento_api, name="tipos_evento_api"),



    # =============================================
    # SOLICITUDES
    # =============================================
    path('solicitudes/', solicitudes_views.lista_solicitudes, name='lista_solicitudes'),
    path('form_solicitud/', solicitudes_views.form_solicitud, name='form_solicitud'),
    path('solicitudes/editar/<int:id_solicitud>/', solicitudes_views.editar_solicitud, name='editar_solicitud'),
    path('solicitudes/eliminar/<int:id_solicitud>/', solicitudes_views.eliminar_solicitud, name='eliminar_solicitud'),
    
    # Aprobaciones de solicitudes
    path('solicitudes/aprobar-jefe/<int:id_solicitud>/', solicitudes_views.aprobar_jefe, name='aprobar_jefe'),
    path('solicitudes/rechazar-jefe/<int:id_solicitud>/', solicitudes_views.rechazar_jefe, name='rechazar_jefe'),
    path('solicitudes/aprobar-director/<int:id_solicitud>/', solicitudes_views.aprobar_director, name='aprobar_director'),
    path('solicitudes/rechazar-director/<int:id_solicitud>/', solicitudes_views.rechazar_director, name='rechazar_director'),
    path('solicitud/<int:id_solicitud>/descargar/', solicitudes_views.descargar_solicitud, name='descargar_solicitud'),
    # =============================================
    # PERFIL DE USUARIO
    # =============================================
    path('perfil/', perfil_views.perfil, name='perfil'),
    path('perfil/editar/', perfil_views.editar_perfil, name='editar_perfil'),
    path('perfil/actualizar-foto/', perfil_views.actualizar_foto_perfil, name='actualizar_foto_perfil'),

    # =============================================
    # LICENCIAS MÉDICAS
    # =============================================
    path('licencias/', licencias_views.lista_licencias, name='lista_licencias'),
    path('form_licencia/', licencias_views.form_licencia, name='form_licencia'),
    path('licencias/editar/<int:id_licencia>/', licencias_views.editar_licencia, name='editar_licencia'),
    path('licencias/eliminar/<int:id_licencia>/', licencias_views.eliminar_licencia, name='eliminar_licencia'),
    path('licencias/detalle/<int:id_licencia>/', licencias_views.detalle_licencia, name='detalle_licencia'),

    # =============================================
    # AUTENTICACIÓN
    # =============================================
    path('login/', base_views.login_personalizado, name='login'),
    path('logout/', base_views.logout_personalizado, name='logout'),
]