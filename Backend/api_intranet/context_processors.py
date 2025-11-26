from .models import Usuario

def rol_usuario(request):
    if request.user.is_authenticated:
        try:
            usuario = Usuario.objects.get(rut=request.user.username)
            return {'rol_usuario': usuario.rol.nombre}
        except Usuario.DoesNotExist:
            return {}
    return {}
