from django.shortcuts import redirect
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/Mascota/moderador/mascotas/')
        return super().dispatch(request, *args, **kwargs)
