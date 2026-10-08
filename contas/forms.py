from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from .models import Usuario


class FormularioCriacaoUsuarioAdmin(AdminUserCreationForm):
    class Meta:
        model = Usuario
        fields = ["email", "nome", "perfil"]


class FormularioAlteracaoUsuarioAdmin(UserChangeForm):
    class Meta:
        model = Usuario
        fields = "__all__"
