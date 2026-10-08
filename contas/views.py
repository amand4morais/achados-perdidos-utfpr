import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import FormularioCadastro, FormularioEntrar

logger = logging.getLogger(__name__)


def ip_do_cliente(request):
    return request.META.get("REMOTE_ADDR", "desconhecido")


class EntrarView(LoginView):
    template_name = "contas/entrar.html"
    authentication_form = FormularioEntrar
    redirect_authenticated_user = True

    def form_valid(self, form):
        resposta = super().form_valid(form)
        logger.info("Login de %s (IP %s)", self.request.user.email, ip_do_cliente(self.request))
        messages.success(self.request, f"Olá, {self.request.user.get_short_name()}!")
        return resposta

    def form_invalid(self, form):
        email = (self.request.POST.get("username") or "").strip().lower()[:254]
        logger.warning("Tentativa de login sem sucesso para %r (IP %s)", email, ip_do_cliente(self.request))
        return super().form_invalid(form)


class CadastrarView(CreateView):
    template_name = "contas/cadastrar.html"
    form_class = FormularioCadastro
    success_url = reverse_lazy("inicio")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("inicio")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        resposta = super().form_valid(form)
        login(self.request, self.object, backend="django.contrib.auth.backends.ModelBackend")
        logger.info("Nova conta criada: %s", self.object.email)
        messages.success(self.request, "Cadastro realizado com sucesso. Bem-vindo(a)!")
        return resposta


class SairView(LogoutView):
    def post(self, request, *args, **kwargs):
        resposta = super().post(request, *args, **kwargs)
        messages.info(request, "Você saiu da sua conta.")
        return resposta
