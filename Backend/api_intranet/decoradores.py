from django.shortcuts import redirect
from .models import Usuario

def rol_requerido(roles_permitidos):
    def decorador(view_func):
        def _wrapped_view(request, *args, **kwargs):

            # obtener usuario de tu tabla usando el rut del User de Django
            try:
                usuario = Usuario.objects.get(rut=request.user.username)
            except Usuario.DoesNotExist:
                return redirect('login')

            if usuario.rol.nombre in roles_permitidos:
                return view_func(request, *args, **kwargs)

            return redirect('inicio')

        return _wrapped_view
    return decorador
