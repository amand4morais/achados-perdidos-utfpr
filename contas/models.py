from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class GerenciadorUsuario(BaseUserManager):
    use_in_migrations = True

    def _criar_usuario(self, email, password, **campos):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        email = self.normalize_email(email).lower()
        usuario = self.model(email=email, **campos)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **campos):
        campos.setdefault("is_staff", False)
        campos.setdefault("is_superuser", False)
        return self._criar_usuario(email, password, **campos)

    def create_superuser(self, email, password=None, **campos):
        campos.setdefault("is_staff", True)
        campos.setdefault("is_superuser", True)
        campos.setdefault("perfil", Usuario.Perfil.ADMIN)
        return self._criar_usuario(email, password, **campos)


class Usuario(AbstractUser):
    class Perfil(models.TextChoices):
        USUARIO = "usuario", "Usuário"
        ADMIN = "admin", "Administrador"

    username = None
    first_name = None
    last_name = None
    nome = models.CharField("nome", max_length=120)
    email = models.EmailField("e-mail", unique=True)
    perfil = models.CharField("perfil", max_length=10, choices=Perfil.choices, default=Perfil.USUARIO)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    objects = GerenciadorUsuario()

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        ordering = ["nome"]

    def __str__(self):
        return self.nome or self.email

    def get_full_name(self):
        return self.nome

    def get_short_name(self):
        return self.nome.split(" ")[0] if self.nome else self.email

    @property
    def eh_admin(self):
        return self.perfil == self.Perfil.ADMIN or self.is_superuser
