from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from api_intranet.models import Licencia, Usuario
from django.utils import timezone
from typing import Optional

def get_usuario_actual(request: HttpRequest) -> Optional[Usuario]:
    """Obtiene el usuario actual desde la sesión"""
    user_id = request.session.get("id_usuario")
    if not user_id:
        return None
    try:
        return Usuario.objects.get(id_usuario=user_id)
    except Usuario.DoesNotExist:
        return None


def lista_licencias(request: HttpRequest) -> HttpResponse:
    """Lista de licencias según el rol del usuario"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    rol_usuario = usuario.id_rol.nombre if usuario.id_rol else "Funcionario"
    
    # Base queryset según permisos
    if rol_usuario in ["Admin", "Director"]:
        # Admin y Director ven todas las licencias
        licencias = Licencia.objects.select_related("id_usuario").all()
    elif rol_usuario == "Jefe de Departamento" and usuario.id_departamento:
        # Jefe ve licencias de su departamento
        licencias = Licencia.objects.select_related("id_usuario").filter(
            id_usuario__id_departamento=usuario.id_departamento
        )
    else:
        # Funcionarios normales ven solo sus propias licencias
        licencias = Licencia.objects.select_related("id_usuario").filter(id_usuario=usuario)

    # Ordenar por fecha más reciente primero
    licencias = licencias.order_by('-fecha_registro')

    # Filtrar por estado si se solicita
    estado_filter = request.GET.get('estado')
    if estado_filter == 'activas':
        licencias = licencias.filter(dia_inicio__lte=timezone.now().date(), dia_fin__gte=timezone.now().date())
    elif estado_filter == 'futuras':
        licencias = licencias.filter(dia_inicio__gt=timezone.now().date())
    elif estado_filter == 'pasadas':
        licencias = licencias.filter(dia_fin__lt=timezone.now().date())

    context = {
        "licencias": licencias,
        "usuario": usuario,
        "rol_usuario": rol_usuario,
        "estado_filter": estado_filter
    }
    return render(request, "pages/licencias/lista_licencias.html", context)


def form_licencia(request: HttpRequest) -> HttpResponse:
    """Crear nueva licencia médica"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")
    
    # Obtener todos los usuarios si es admin/director para el select
    usuarios = None
    if usuario.id_rol and (usuario.id_rol.nombre == "Admin" or usuario.id_rol.nombre == "Director"):
        usuarios = Usuario.objects.all()

    if request.method == "POST":
        dia_inicio_str = request.POST.get("dia_inicio", "").strip()
        dia_fin_str = request.POST.get("dia_fin", "").strip()
        imagen = request.FILES.get("imagen")

        # Validaciones básicas
        if not all([dia_inicio_str, dia_fin_str, imagen]):
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, "pages/licencias/form_licencia.html", {
                "data": {
                    "dia_inicio": dia_inicio_str,
                    "dia_fin": dia_fin_str
                }
            })

        try:
            # Convertir strings a date
            from datetime import datetime
            dia_inicio = datetime.strptime(dia_inicio_str, '%Y-%m-%d').date()
            dia_fin = datetime.strptime(dia_fin_str, '%Y-%m-%d').date()

            # Crear la licencia con validaciones
            licencia = Licencia(
                dia_inicio=dia_inicio,
                dia_fin=dia_fin,
                imagen=imagen,
                id_usuario=usuario,
                fecha_registro=timezone.now()
            )
            
            # Aplicar validaciones del modelo
            licencia.full_clean()
            licencia.save()
            
            messages.success(request, "Licencia médica registrada exitosamente.")
            return redirect("lista_licencias")
            
        except ValueError:
            messages.error(request, "Formato de fecha inválido. Use YYYY-MM-DD.")
            return render(request, "pages/licencias/form_licencia.html", {
                "data": {
                    "dia_inicio": dia_inicio_str,
                    "dia_fin": dia_fin_str
                }
            })
        except Exception as e:
            messages.error(request, f"Error al registrar la licencia: {str(e)}")
            return render(request, "pages/licencias/form_licencia.html", {
                "data": {
                    "dia_inicio": dia_inicio_str,
                    "dia_fin": dia_fin_str
                }
            })
    # GET request - mostrar formulario con datos necesarios
    context = {
        "usuarios": usuarios,
        "rol_usuario": usuario.id_rol.nombre if usuario.id_rol else "Funcionario",
        "usuario": usuario,
        "today": timezone.now().date()  # También necesitas esta variable para el min date
    }
    return render(request, "pages/licencias/form_licencia.html", context)   

def editar_licencia(request: HttpRequest, id_licencia: int) -> HttpResponse:
    """Editar licencia existente"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    licencia = get_object_or_404(Licencia, id_licencia=id_licencia)

    # Verificar permisos: solo el dueño de la licencia o admin puede editarla
    if licencia.id_usuario.id_usuario != usuario.id_usuario and not (usuario.id_rol and usuario.id_rol.nombre == 'Admin'):
        messages.error(request, "No tienes permisos para editar esta licencia.")
        return redirect("lista_licencias")

    # No permitir editar licencias pasadas
    if licencia.dia_fin < timezone.now().date():
        messages.error(request, "No se pueden editar licencias que ya han finalizado.")
        return redirect("lista_licencias")

    if request.method == "POST":
        dia_inicio_str = request.POST.get("dia_inicio", "").strip()
        dia_fin_str = request.POST.get("dia_fin", "").strip()
        imagen = request.FILES.get("imagen")

        if not dia_inicio_str or not dia_fin_str:
            messages.error(request, "Las fechas de inicio y fin son obligatorias.")
            return render(request, "pages/licencias/editar_licencia.html", {"licencia": licencia})

        try:
            # Convertir strings a date
            from datetime import datetime
            dia_inicio = datetime.strptime(dia_inicio_str, '%Y-%m-%d').date()
            dia_fin = datetime.strptime(dia_fin_str, '%Y-%m-%d').date()

            # Actualizar campos
            licencia.dia_inicio = dia_inicio
            licencia.dia_fin = dia_fin
            
            if imagen:
                licencia.imagen = imagen

            # Aplicar validaciones del modelo
            licencia.full_clean()
            licencia.save()
            
            messages.success(request, "Licencia actualizada exitosamente.")
            return redirect("lista_licencias")
            
        except ValueError:
            messages.error(request, "Formato de fecha inválido. Use YYYY-MM-DD.")
            return render(request, "pages/licencias/editar_licencia.html", {"licencia": licencia})
        except Exception as e:
            messages.error(request, f"Error al actualizar la licencia: {str(e)}")
            return render(request, "pages/licencias/editar_licencia.html", {"licencia": licencia})

    # GET request - mostrar formulario con datos actuales
    return render(request, "pages/licencias/editar_licencia.html", {"licencia": licencia})

def eliminar_licencia(request: HttpRequest, id_licencia: int) -> HttpResponse:
    """Eliminar licencia"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    licencia = get_object_or_404(Licencia, id_licencia=id_licencia)

    # Verificar permisos: solo el dueño de la licencia o admin puede eliminarla
    if licencia.id_usuario.id_usuario != usuario.id_usuario and not (usuario.id_rol and usuario.id_rol.nombre == 'Admin'):
        messages.error(request, "No tienes permisos para eliminar esta licencia.")
        return redirect("lista_licencias")

    if request.method == "POST":
        try:
            licencia.delete()
            messages.success(request, "Licencia eliminada exitosamente.")
            return redirect("lista_licencias")
        except Exception as e:
            messages.error(request, f"Error al eliminar la licencia: {str(e)}")
            return redirect("lista_licencias")

    # GET request - mostrar confirmación
    return render(request, "pages/licencias/confirmar_eliminar.html", {"licencia": licencia})


def detalle_licencia(request: HttpRequest, id_licencia: int) -> HttpResponse:
    """Vista detallada de una licencia específica"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    licencia = get_object_or_404(Licencia, id_licencia=id_licencia)

    # Verificar permisos de visualización
    rol_usuario = usuario.id_rol.nombre if usuario.id_rol else "Funcionario"
    puede_ver = (
        licencia.id_usuario.id_usuario == usuario.id_usuario or
        rol_usuario in ["Admin", "Director"] or
        (rol_usuario == "Jefe de Departamento" and 
            licencia.id_usuario.id_departamento == usuario.id_departamento)
    )

    if not puede_ver:
        messages.error(request, "No tienes permisos para ver esta licencia.")
        return redirect("lista_licencias")

    context = {
        "licencia": licencia,
        "usuario": usuario,
        "puede_editar": (
            licencia.id_usuario.id_usuario == usuario.id_usuario or
            rol_usuario in ["Admin", "Director"]
        )
    }
    return render(request, "pages/licencias/detalle_licencia.html", context)