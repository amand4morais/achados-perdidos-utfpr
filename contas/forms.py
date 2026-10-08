from django import forms
from django.contrib.auth.forms import (
    AdminUserCreationForm,
    AuthenticationForm,
    BaseUserCreationForm,
    UserChangeForm,
)

from .models import Usuario


class CamposBootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nome, campo in self.fields.items():
            widget = campo.widget
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                classe = "form-check-input"
            elif isinstance(widget, forms.Select):
                classe = "form-select"
            else:
                classe = "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {classe}".strip()

    def full_clean(self):
        super().full_clean()
        for nome in self.errors:
            if nome in self.fields:
                widget = self.fields[nome].widget
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} is-invalid".strip()
                widget.attrs["aria-invalid"] = "true"


class FormularioEntrar(CamposBootstrapMixin, AuthenticationForm):
    error_messages = {
        "invalid_login": "E-mail ou senha incorretos.",
        "inactive": "Esta conta está desativada.",
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["username"].label = "E-mail"
        self.fields["username"].widget.input_type = "email"
        self.fields["username"].widget.attrs["autocomplete"] = "email"
        self.fields["password"].label = "Senha"

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()


class FormularioCadastro(CamposBootstrapMixin, BaseUserCreationForm):
    class Meta:
        model = Usuario
        fields = ["nome", "email"]
        widgets = {
            "nome": forms.TextInput(attrs={"autocomplete": "name", "autofocus": True}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Senha"
        self.fields["password1"].help_text = "Use pelo menos 8 caracteres, sem ser só números e diferente do seu nome ou e-mail."
        self.fields["password2"].label = "Confirme a senha"
        self.fields["password2"].help_text = ""

    def validate_password_for_user(self, user, **kwargs):
        super().validate_password_for_user(user, password_field_name="password1")

    def clean_nome(self):
        nome = " ".join(self.cleaned_data["nome"].split())
        if len(nome) < 3:
            raise forms.ValidationError("Informe seu nome completo.")
        return nome

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email


class FormularioCriacaoUsuarioAdmin(AdminUserCreationForm):
    class Meta:
        model = Usuario
        fields = ["email", "nome", "perfil"]


class FormularioAlteracaoUsuarioAdmin(UserChangeForm):
    class Meta:
        model = Usuario
        fields = "__all__"
