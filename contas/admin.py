from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import FormularioAlteracaoUsuarioAdmin, FormularioCriacaoUsuarioAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = FormularioAlteracaoUsuarioAdmin
    add_form = FormularioCriacaoUsuarioAdmin
    ordering = ["nome"]
    list_display = ["nome", "email", "perfil", "is_active", "date_joined"]
    list_filter = ["perfil", "is_active"]
    search_fields = ["nome", "email"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Dados pessoais", {"fields": ["nome", "perfil"]}),
        ("Permissões", {"fields": ["is_active", "is_staff", "is_superuser", "groups", "user_permissions"]}),
        ("Datas", {"fields": ["last_login", "date_joined"]}),
    ]
    add_fieldsets = [
        (None, {
            "classes": ["wide"],
            "fields": ["nome", "email", "perfil", "password1", "password2"],
        }),
    ]
