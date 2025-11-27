from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse
from api_intranet.models import Usuario, RolUsuario, Departamento, Cargo

def lista_funcionarios(request: HttpRequest) -> HttpResponse:
    # Obtener filtro por inicial desde GET
    inicial = request.GET.get("inicial")

    if inicial:
        funcionarios = Usuario.objects.filter(nombre__istartswith=inicial)
    else:
        funcionarios = Usuario.objects.all()

    # Obtener cargos correctamente
    cargos = Cargo.objects.all()

    # Obtener rol del usuario (ajusta según tu sistema de roles)
    rol_usuario = request.session.get("rol")  # ejemplo

    return render(request, "pages/funcionarios/lista_funcionarios.html", {
        "funcionarios": funcionarios,
        "rol_usuario": rol_usuario,
        "cargos": cargos
    })

def form_funcionario(request):
    # Obtener datos para mostrar en el formulario
    roles = RolUsuario.objects.all()
    departamentos = Departamento.objects.all()
    cargos = Cargo.objects.all()

    # Si el formulario fue enviado
    if request.method == "POST":
        rut = request.POST.get("rut")
        dv = request.POST.get("dv")
        nombre = request.POST.get("nombre")
        telefono = request.POST.get("telefono")
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")

        id_rol = request.POST.get("id_rol") or None
        id_departamento = request.POST.get("id_departamento") or None
        id_cargo = request.POST.get("id_cargo") or None

        Usuario.objects.create(
            rut=rut,
            dv=dv,
            nombre=nombre,
            telefono=telefono,
            correo=correo,
            contrasena=contrasena,
            id_rol_id=id_rol,
            id_departamento_id=id_departamento,
            id_cargo_id=id_cargo
        )

        return redirect("lista_funcionarios")  # vuelve al listado

    # GET (cuando abre la página)
    return render(
        request,
        "pages/funcionarios/form_funcionario.html",
        {
            "roles": roles,
            "departamentos": departamentos,
            "cargos": cargos
        }
    )




def editar_funcionario(request, id_usuario):
    funcionario = get_object_or_404(Usuario, id_usuario=id_usuario)

    roles = RolUsuario.objects.all()
    departamentos = Departamento.objects.all()
    cargos = Cargo.objects.all()

    if request.method == "POST":
        funcionario.rut = request.POST.get("rut")
        funcionario.dv = request.POST.get("dv")
        funcionario.nombre = request.POST.get("nombre")
        funcionario.telefono = request.POST.get("telefono")
        funcionario.correo = request.POST.get("correo")
        funcionario.contrasena = request.POST.get("contrasena")

        funcionario.id_rol_id = request.POST.get("id_rol") or None
        funcionario.id_departamento_id = request.POST.get("id_departamento") or None
        funcionario.id_cargo_id = request.POST.get("id_cargo") or None

        funcionario.save()

        return redirect("lista_funcionarios")

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

def eliminar_funcionario(request, id_usuario):
    funcionario = get_object_or_404(Usuario, id_usuario=id_usuario)

    if request.method == "POST":
        funcionario.delete()
        return redirect("lista_funcionarios")

    return render(request, "pages/funcionarios/eliminar_funcionario.html", {"funcionario": funcionario})
