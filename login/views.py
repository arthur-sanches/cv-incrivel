from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

from .forms import EmailAuthenticationForm


class CustomLoginView(LoginView):
    template_name = "login/login.html"
    authentication_form = EmailAuthenticationForm

    def get_success_url(self):
        return "/generate_cv/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/generate_cv/")
        return super().dispatch(request, *args, **kwargs)


def logout_view(request):
    logout(request)
    return redirect("/login/")
