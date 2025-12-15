from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from api_intranet.models import Usuario, RolUsuario, Departamento, Cargo
from django.contrib.auth.decorators import login_required
from typing import Optional
from django.db import transaction
from django.core.exceptions import ValidationError 

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
    # TODOS pueden ver a todos los funcionarios
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
    funcionarios = (
        funcionarios
        .select_related('id_rol', 'id_departamento', 'id_cargo')
        .prefetch_related('perfil_set')
        .order_by('nombre')
    )



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

        # Validaciones mínimas
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
            with transaction.atomic():
                funcionario = Usuario(
                    rut=int(rut),
                    dv=dv,
                    nombre=nombre,
                    telefono=telefono or None,
                    correo=correo or None,
                    contrasena=contrasena,
                    id_rol_id=int(id_rol) if id_rol and id_rol.isdigit() else None,
                    id_departamento_id=int(id_departamento) if id_departamento and id_departamento.isdigit() else None,
                    id_cargo_id=int(id_cargo) if id_cargo and id_cargo.isdigit() else None
                )

                funcionario.full_clean()
                funcionario.save()

                # -------- LÓGICA JEFE DE DEPARTAMENTO --------
                if id_rol == "3" and id_departamento and id_departamento.isdigit():
                    depto = Departamento.objects.filter(pk=int(id_departamento)).first()

                    if depto:
                        # 1) Si el usuario era jefe en otro departamento, limpiarlo
                        otros_deptos = Departamento.objects.filter(
                            jefe_departamento=funcionario
                        ).exclude(pk=depto.pk)

                        for d in otros_deptos:
                            d.jefe_departamento = None
                            d.save()

                        # 2) Asignar como jefe del nuevo departamento
                        depto.jefe_departamento = funcionario
                        depto.save()

                        # 3) Quitar jefatura al jefe anterior
                        jefe_anterior = Usuario.objects.filter(
                            id_rol__nombre="Jefe de Departamento",
                            id_departamento=depto
                        ).exclude(id_usuario=funcionario.id_usuario).first()

                        if jefe_anterior:
                            jefe_anterior.id_rol = RolUsuario.objects.get(nombre="Funcionario")
                            jefe_anterior.save()
                # ---------------------------------------------

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

    return render(request, "pages/funcionarios/form_funcionario.html", {
        "roles": roles,
        "departamentos": departamentos,
        "cargos": cargos
    })

def editar_funcionario(request: HttpRequest, id_usuario: int) -> HttpResponse:
    usuario = get_usuario_actual(request)
    if not usuario:
        return redirect("login")

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
            # ⭐ CAPTURAR VALORES ORIGINALES PRIMERO (antes de modificar)
            rut_original = funcionario.rut
            dv_original = (funcionario.dv or "").upper().strip()
            
            # Ahora sí procesar los inputs
            rut_str = request.POST.get("rut")
            dv_input = request.POST.get("dv", "")
            nombre_input = request.POST.get("nombre", "")
            telefono_input = request.POST.get("telefono", "")
            correo_input = request.POST.get("correo", "")
            nueva_contrasena = request.POST.get("contrasena", "").strip()

            id_rol = request.POST.get("id_rol")
            id_departamento = request.POST.get("id_departamento")
            id_cargo = request.POST.get("id_cargo")

            if rut_str and rut_str.isdigit():
                funcionario.rut = int(rut_str)

            if dv_input:
                funcionario.dv = dv_input.upper().strip()

            if nombre_input:
                funcionario.nombre = nombre_input.strip()

            funcionario.telefono = telefono_input.strip() or None
            funcionario.correo = correo_input.strip() or None

            if nueva_contrasena:
                funcionario.contrasena = nueva_contrasena

            # -------- FK CORRECTAS (sin _id) --------
            funcionario.id_rol = RolUsuario.objects.filter(pk=id_rol).first() if id_rol else None
            funcionario.id_departamento = Departamento.objects.filter(pk=id_departamento).first() if id_departamento else None
            funcionario.id_cargo = Cargo.objects.filter(pk=id_cargo).first() if id_cargo else None
            
            with transaction.atomic():
                # Determinar si RUT o DV cambiaron comparando con originales
                rut_cambio = (funcionario.rut != rut_original)
                dv_cambio = (funcionario.dv != dv_original)

                # Solo validar rut/dv si realmente cambiaron
                if rut_cambio or dv_cambio:
                    # Si cambió, validar todo incluyendo RUT/DV
                    funcionario.full_clean()
                else:
                    # Si NO cambió, validar campos individuales SIN llamar a clean()
                    # porque el método clean() del modelo valida RUT/DV sin importar exclude
                    funcionario.clean_fields(exclude=["rut", "dv"])
                    # NO llamamos a funcionario.clean() para evitar validación de RUT/DV
                    funcionario.validate_unique()

                funcionario.save()

                # -------- LÓGICA JEFE DE DEPARTAMENTO --------
                if funcionario.id_rol and funcionario.id_rol.nombre == "Jefe de Departamento":

                    otro_depto = Departamento.objects.filter(
                        jefe_departamento=funcionario
                    ).exclude(
                        pk=funcionario.id_departamento.pk if funcionario.id_departamento else None
                    ).first()

                    if otro_depto:
                        otro_depto.jefe_departamento = None
                        otro_depto.save()

                    if funcionario.id_departamento:
                        depto = funcionario.id_departamento

                        if depto.jefe_departamento and depto.jefe_departamento != funcionario:
                            depto.jefe_departamento = None
                            depto.save()

                        depto.jefe_departamento = funcionario
                        depto.save()

                        jefe_anterior = Usuario.objects.filter(
                            id_rol__nombre="Jefe de Departamento",
                            id_departamento=depto
                        ).exclude(id_usuario=funcionario.id_usuario).first()

                        if jefe_anterior:
                            jefe_anterior.id_rol = RolUsuario.objects.get(nombre="Funcionario")
                            jefe_anterior.save()

                else:
                    for d in Departamento.objects.filter(jefe_departamento=funcionario):
                        d.jefe_departamento = None
                        d.save()

            messages.success(request, f"Funcionario {funcionario.nombre} actualizado exitosamente.")
            return redirect("lista_funcionarios")

        except ValidationError as e:
            print("VALIDATION ERROR:", e.message_dict if hasattr(e, "message_dict") else str(e))
            detalle = e.message_dict if hasattr(e, "message_dict") else str(e)
            messages.error(request, f"Error de validación: {detalle}")
            return render(request, "pages/funcionarios/editar_funcionario.html", {
                "funcionario": funcionario,
                "roles": roles,
                "departamentos": departamentos,
                "cargos": cargos,
            })

        except Exception as e:
            print("ERROR:", str(e))
            messages.error(request, f"Error al actualizar funcionario: {str(e)}")
            return render(request, "pages/funcionarios/editar_funcionario.html", {
                "funcionario": funcionario,
                "roles": roles,
                "departamentos": departamentos,
                "cargos": cargos,
            })

    return render(request, "pages/funcionarios/editar_funcionario.html", {
        "funcionario": funcionario,
        "roles": roles,
        "departamentos": departamentos,
        "cargos": cargos,
    })
    
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
            Departamento.objects.filter(jefe_departamento=funcionario).update(jefe_departamento=None)
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