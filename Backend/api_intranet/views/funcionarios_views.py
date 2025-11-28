from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from api_intranet.models import Usuario, RolUsuario, Departamento, Cargo
from django.contrib.auth.decorators import login_required
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


def lista_funcionarios(request: HttpRequest) -> HttpResponse:
    """Lista de funcionarios con filtros y permisos por rol"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    # Verificar permisos según rol
    rol_usuario = getattr(usuario.id_rol, 'nombre', 'Funcionario') if usuario.id_rol else "Funcionario"
    
    # Base queryset
    if rol_usuario == "Director":
        # Admin y Director ven todos los funcionarios
        funcionarios = Usuario.objects.all()
    elif rol_usuario == "Jefe_depto" and usuario.id_departamento:
        # Jefe ve solo funcionarios de su departamento
        funcionarios = Usuario.objects.filter(id_departamento=usuario.id_departamento)
    else:
        # Funcionarios normales ven lista básica (solo info pública)
        funcionarios = Usuario.objects.all()

    # Aplicar filtros
    inicial = request.GET.get("inicial")
    if inicial:
        funcionarios = funcionarios.filter(nombre__istartswith=inicial)

    departamento_filter = request.GET.get("departamento")
    if departamento_filter:
        funcionarios = funcionarios.filter(id_departamento_id=departamento_filter)

    cargo_filter = request.GET.get("cargo")
    if cargo_filter:
        funcionarios = funcionarios.filter(id_cargo_id=cargo_filter)

    # Optimizar consultas
    funcionarios = funcionarios.select_related('id_rol', 'id_departamento', 'id_cargo').order_by('nombre')

    # Datos para filtros
    cargos = Cargo.objects.all()
    departamentos = Departamento.objects.all()

    context = {
        "funcionarios": funcionarios,
        "rol_usuario": rol_usuario,
        "cargos": cargos,
        "departamentos": departamentos,
        "usuario": usuario
    }
    return render(request, "pages/funcionarios/lista_funcionarios.html", context)


def form_funcionario(request: HttpRequest) -> HttpResponse:
    """Crear nuevo funcionario (solo Admin)"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    # Solo Admin puede crear funcionarios
    rol_nombre = getattr(usuario.id_rol, 'nombre', '') if usuario.id_rol else ''
    if rol_nombre != "Director":
        messages.error(request, "No tienes permisos para crear funcionarios.")
        return redirect("lista_funcionarios")

    # Obtener datos para mostrar en el formulario
    roles = RolUsuario.objects.all()
    departamentos = Departamento.objects.all()
    cargos = Cargo.objects.all()

    if request.method == "POST":
        rut = request.POST.get("rut", "").strip()
        dv = request.POST.get("dv", "").strip().upper()
        nombre = request.POST.get("nombre", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        correo = request.POST.get("correo", "").strip()
        contrasena = request.POST.get("contrasena", "").strip()

        id_rol = request.POST.get("id_rol") or None
        id_departamento = request.POST.get("id_departamento") or None
        id_cargo = request.POST.get("id_cargo") or None

        # Validaciones básicas
        if not all([rut, dv, nombre, contrasena]):
            messages.error(request, "RUT, DV, nombre y contraseña son obligatorios.")
            return render(request, "pages/funcionarios/form_funcionario.html", {
                "roles": roles,
                "departamentos": departamentos,
                "cargos": cargos,
                "data": request.POST
            })
            
        if not rut.isdigit():
            messages.error(request, "El RUT debe contener solo números.")
            return render(request, "pages/funcionarios/form_funcionario.html", {
                "roles": roles,
                "departamentos": departamentos,
                "cargos": cargos,
                "data": request.POST
            })

        try:
            # Crear el funcionario con validaciones
            funcionario = Usuario(
                rut=int(rut),  # Ahora es seguro porque validamos que es dígito
                dv=dv,
                nombre=nombre,
                telefono=telefono or None,
                correo=correo or None,
                contrasena=contrasena,
                # CORREGIDO: Asignación segura de ForeignKeys
                id_rol_id=int(id_rol) if id_rol and id_rol.isdigit() else None,
                id_departamento_id=int(id_departamento) if id_departamento and id_departamento.isdigit() else None,
                id_cargo_id=int(id_cargo) if id_cargo and id_cargo.isdigit() else None
            )
            # Aplicar validaciones del modelo
            funcionario.full_clean()
            funcionario.save()
            
            messages.success(request, f"Funcionario {nombre} creado exitosamente.")
            return redirect("lista_funcionarios")
            
        except Exception as e:
            messages.error(request, f"Error al crear funcionario: {str(e)}")
            return render(request, "pages/funcionarios/form_funcionario.html", {
                "roles": roles,
                "departamentos": departamentos,
                "cargos": cargos,
                "data": request.POST
            })

    # GET request - mostrar formulario vacío
    return render(
        request,
        "pages/funcionarios/form_funcionario.html",
        {
            "roles": roles,
            "departamentos": departamentos,
            "cargos": cargos
        }
    )

def editar_funcionario(request: HttpRequest, id_usuario: int) -> HttpResponse:
    """Editar funcionario existente (solo Admin)"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    # Solo Admin puede editar funcionarios
    rol_nombre = getattr(usuario.id_rol, 'nombre', '') if usuario.id_rol else ''
    if rol_nombre != "Director":
        messages.error(request, "No tienes permisos para editar funcionarios.")
        return redirect("lista_funcionarios")

    funcionario = get_object_or_404(Usuario, id_usuario=id_usuario)

    roles = RolUsuario.objects.all()
    departamentos = Departamento.objects.all()
    cargos = Cargo.objects.all()

    if request.method == "POST":
        try:
            # Conversión segura de RUT
            rut_str = request.POST.get("rut")
            if rut_str and rut_str.isdigit():
                funcionario.rut = int(rut_str)
            
            # Métodos seguros en strings
            dv_input = request.POST.get("dv", "")
            funcionario.dv = dv_input.upper().strip() if dv_input else getattr(funcionario, 'dv', '')
            
            nombre_input = request.POST.get("nombre", "")
            funcionario.nombre = nombre_input.strip() if nombre_input else getattr(funcionario, 'nombre', '')
            
            funcionario.telefono = request.POST.get("telefono", "").strip() or None
            funcionario.correo = request.POST.get("correo", "").strip() or None
            
            # Solo actualizar contraseña si se proporcionó una nueva
            nueva_contrasena = request.POST.get("contrasena", "").strip()
            if nueva_contrasena:
                funcionario.contrasena = nueva_contrasena

            # CORRECCIÓN: Asignación segura de ForeignKeys usando objetos completos
            id_rol = request.POST.get("id_rol")
            id_departamento = request.POST.get("id_departamento")
            id_cargo = request.POST.get("id_cargo")
            
            # Asignar objetos ForeignKey completos
            if id_rol and id_rol.isdigit():
                try:
                    funcionario.id_rol = RolUsuario.objects.get(pk=int(id_rol))
                except RolUsuario.DoesNotExist:
                    funcionario.id_rol = None
            else:
                funcionario.id_rol = None

            if id_departamento and id_departamento.isdigit():
                try:
                    funcionario.id_departamento = Departamento.objects.get(pk=int(id_departamento))
                except Departamento.DoesNotExist:
                    funcionario.id_departamento = None
            else:
                funcionario.id_departamento = None

            if id_cargo and id_cargo.isdigit():
                try:
                    funcionario.id_cargo = Cargo.objects.get(pk=int(id_cargo))
                except Cargo.DoesNotExist:
                    funcionario.id_cargo = None
            else:
                funcionario.id_cargo = None

            # Aplicar validaciones del modelo
            funcionario.full_clean()
            funcionario.save()
            
            messages.success(request, f"Funcionario {funcionario.nombre} actualizado exitosamente.")
            return redirect("lista_funcionarios")
            
        except Exception as e:
            messages.error(request, f"Error al actualizar funcionario: {str(e)}")
            return render(request, "pages/funcionarios/editar_funcionario.html", {
                "funcionario": funcionario,
                "roles": roles,
                "departamentos": departamentos,
                "cargos": cargos,
            })

    # GET request - mostrar formulario con datos actuales
    return render(
        request,
        "pages/funcionarios/editar_funcionario.html",
        {
            "funcionario": funcionario,
            "roles": roles,
            "departamentos": departamentos,
            "cargos": cargos,
        }
    )



def eliminar_funcionario(request: HttpRequest, id_usuario: int) -> HttpResponse:
    """Eliminar funcionario (solo Admin)"""
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

    # Solo Admin puede eliminar funcionarios
    rol_nombre = getattr(usuario.id_rol, 'nombre', '') if usuario.id_rol else ''
    if rol_nombre != "Director":
        messages.error(request, "No tienes permisos para eliminar funcionarios.")
        return redirect("lista_funcionarios")

    funcionario = get_object_or_404(Usuario, id_usuario=id_usuario)

    # Prevenir auto-eliminación
    if funcionario.id_usuario == usuario.id_usuario:
        messages.error(request, "No puedes eliminar tu propio usuario.")
        return redirect("lista_funcionarios")

    if request.method == "POST":
        try:
            nombre_funcionario = funcionario.nombre
            funcionario.delete()
            messages.success(request, f"Funcionario {nombre_funcionario} eliminado exitosamente.")
            return redirect("lista_funcionarios")
        except Exception as e:
            messages.error(request, f"Error al eliminar funcionario: {str(e)}")
            return redirect("lista_funcionarios")

    # GET request - mostrar confirmación
    return render(request, "pages/funcionarios/eliminar_funcionario.html", {
        "funcionario": funcionario
    })