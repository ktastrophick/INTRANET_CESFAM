"""
Vistas base de la intranet (páginas generales como inicio e index).
"""

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from api_intranet.models import Usuario, Avisos, Documento, InicioRegistrado, Licencia, Calendario
from django.contrib import messages
from django.contrib.auth import logout 


from typing import Optional

def get_usuario_actual(request: HttpRequest) -> Optional[Usuario]:
    """Obtiene el usuario actual desde la sesión"""
    user_id = request.session.get("id_usuario")
    print(f"=== DEBUG get_usuario_actual ===")
    print(f"Session ID: {user_id}")
    print(f"Session keys: {list(request.session.keys())}")
    print(f"Session data: {dict(request.session)}")
    
    if not user_id:
        print("NO hay user_id en sesión - retornando None")
        return None
    
    try:
        usuario = Usuario.objects.get(id_usuario=user_id)
        print(f"Usuario encontrado: {usuario.nombre} (ID: {usuario.id_usuario})")
        return usuario
    except Usuario.DoesNotExist:
        print(f"Usuario con ID {user_id} no existe en BD - retornando None")
        return None
    except Exception as e:
        print(f"Error al buscar usuario: {e} - retornando None")
        return None

def inicio(request: HttpRequest) -> HttpResponse:
    """
    Vista de la página pública de inicio.

    - Si el usuario está en sesión → redirige al dashboard (index).
    - Si NO está en sesión → muestra la portada (landing).

    Plantilla: 'pages/inicio.html'
    """
    print("=== DEBUG INICIO ===")
    print(f"URL solicitada: {request.path}")
    
    usuario = get_usuario_actual(request)
    
    if usuario:
        print(f"USUARIO ENCONTRADO: {usuario.nombre} - Redirigiendo a index")
        return redirect("index")
    else:
        print("NO hay usuario - Mostrando página de inicio")
        return render(request, "pages/inicio.html")


def index(request: HttpRequest) -> HttpResponse:
    """
    Vista del dashboard principal.

    - Solo accesible si el usuario está autenticado.
    - Muestra información resumida y avisos.

    Plantilla: 'pages/index.html'
    """
    usuario = get_usuario_actual(request)
    if not usuario:
        messages.error(request, "Debes iniciar sesión para acceder al dashboard.")
        return redirect("login")

    try:
        # Últimos 5 avisos
        avisos = Avisos.objects.all().order_by("-fecha_registro")[:5]

        # Documentos subidos por el usuario
        documentos_count = Documento.objects.filter(subido_por=usuario).count()

        # Solicitudes pendientes del usuario
        from api_intranet.models import Solicitud, EstadoSolicitud

        estado_pendiente = EstadoSolicitud.objects.get(nombre="Pendiente")
        estado_aprobada = EstadoSolicitud.objects.get(nombre="Aprobada")
        estado_rechazada = EstadoSolicitud.objects.get(nombre="Rechazada")

        solicitudes_pendientes = Solicitud.objects.filter(
            id_usuario=usuario,
            estado_solicitud=estado_pendiente
        ).count()

        solicitudes_aceptadas = Solicitud.objects.filter(
            id_usuario=usuario,
            estado_solicitud=estado_aprobada
        ).count()

        solicitudes_rechazadas = Solicitud.objects.filter(
            id_usuario=usuario,
            estado_solicitud=estado_rechazada
        ).count()

        solicitudes_recibidas = (
            solicitudes_pendientes +
            solicitudes_aceptadas +
            solicitudes_rechazadas
        )
        # --- FIN BLOQUE SOLICITUDES ---

        # Licencias activas del usuario
        from datetime import date, timedelta
        licencias_activas = Licencia.objects.filter(
            id_usuario=usuario,
            dia_inicio__lte=date.today(),
            dia_fin__gte=date.today()
        ).count
        # Eventos próximos del usuario (próximos 7 días)
        from datetime import timedelta
        eventos_proximos = Calendario.objects.filter(
            id_usuario=usuario,
            fecha__range=[date.today(), date.today() + timedelta(days=7)]
        ).count()

        # Registrar inicio de sesión (log de actividad)
        InicioRegistrado.objects.create(id_usuario=usuario)

        context = {
            "usuario": usuario,
            "avisos": avisos,
            "documentos_count": documentos_count,
            "solicitudes_pendientes": solicitudes_pendientes,
            "licencias_activas": licencias_activas,
            "eventos_proximos": eventos_proximos,
            "rol": usuario.id_rol.nombre if usuario.id_rol else "Funcionario",
        }
        
        return render(request, "pages/index.html", context)

    except Exception as e:
        # En caso de error, mostrar dashboard básico
        messages.warning(request, "Algunos datos no pudieron cargarse correctamente.")
        context = {
            "usuario": usuario,
            "rol": usuario.id_rol.nombre if usuario.id_rol else "Funcionario",
        }
        return render(request, "pages/index.html", context)


def dashboard_admin(request: HttpRequest) -> HttpResponse:
    """
    Dashboard específico para administradores.

    - Solo accesible para usuarios con rol Admin.
    - Muestra estadísticas y herramientas administrativas.
    """
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    # Verificar que sea admin
    if not usuario.id_rol or usuario.id_rol.nombre != "Admin":
        messages.error(request, "No tienes permisos para acceder al panel de administración.")
        return redirect("index")

    try:
        # Estadísticas para admin
        from django.db.models import Count
        from api_intranet.models import Solicitud, EstadoSolicitud
        
        total_usuarios = Usuario.objects.count()
        total_documentos = Documento.objects.count()
        
        # Solicitudes por estado
        solicitudes_por_estado = Solicitud.objects.values(
            'estado_solicitud__nombre'
        ).annotate(
            total=Count('id_solicitud')
        )
        
        # Usuarios por departamento
        usuarios_por_depto = Usuario.objects.values(
            'id_departamento__nombre'
        ).annotate(
            total=Count('id_usuario')
        ).exclude(id_departamento__isnull=True)

        context = {
            "usuario": usuario,
            "total_usuarios": total_usuarios,
            "total_documentos": total_documentos,
            "solicitudes_por_estado": solicitudes_por_estado,
            "usuarios_por_depto": usuarios_por_depto,
        }
        
        return render(request, "pages/dashboard_admin.html", context)

    except Exception as e:
        messages.error(request, f"Error al cargar el dashboard administrativo: {str(e)}")
        return redirect("index")

def login_personalizado(request: HttpRequest) -> HttpResponse:
    """Vista de login personalizada que integra ambos sistemas"""
    # Si ya está autenticado, redirigir al index
    usuario_actual = get_usuario_actual(request)
    if usuario_actual:
        messages.info(request, "Ya tienes una sesión activa")
        return redirect('index')
    
    if request.method == 'POST':
        rut_str = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Validar que no estén vacíos
        if not rut_str or not password:
            messages.error(request, "RUT y contraseña son obligatorios")
            return render(request, 'pages/autenticacion.html')
        
        try:
            # Convertir RUT a número (eliminar puntos y guión si existen)
            rut_limpio = rut_str.replace('.', '').replace('-', '')
            if rut_limpio[:-1].isdigit():
                rut_numero = int(rut_limpio[:-1])
                dv = rut_limpio[-1].upper()
            else:
                messages.error(request, "Formato de RUT inválido")
                return render(request, 'pages/autenticacion.html')
            
            # Buscar usuario en tu sistema
            usuario = Usuario.objects.get(rut=rut_numero, dv=dv, contrasena=password)
            
            # Guardar en sesión
            request.session['id_usuario'] = usuario.id_usuario
            request.session['usuario_nombre'] = usuario.nombre
            request.session['usuario_rol'] = usuario.id_rol.nombre if usuario.id_rol else "Funcionario"
            
            messages.success(request, f"¡Bienvenido/a {usuario.nombre}!")
            return redirect('index')
            
        except Usuario.DoesNotExist:
            messages.error(request, "RUT o contraseña incorrectos")
        except ValueError:
            messages.error(request, "Formato de RUT inválido")
        except Exception as e:
            messages.error(request, f"Error al iniciar sesión: {str(e)}")
    
    # GET request - mostrar formulario
    return render(request, 'pages/autenticacion.html')


def logout_personalizado(request):
    # Cerrar sesión de Django (por si acaso)
    logout(request)
    # Limpiar TODA la sesión de la intranet
    request.session.flush()
    messages.info(request, "Sesión cerrada correctamente.")
    # Volver a la portada (inicio)
    return redirect('inicio')