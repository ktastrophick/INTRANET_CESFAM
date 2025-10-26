# api_intranet/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('documentos/', views.documentos, name='documentos'),
    path('calendario/', views.calendario, name='calendario'),
    path('solicitudes/', views.solicitudes, name='solicitudes'),
    path('perfil/', views.perfil, name='perfil'),

    # Auth
    path('login/',  auth_views.LoginView.as_view(
        template_name='pages/autenticacion.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
