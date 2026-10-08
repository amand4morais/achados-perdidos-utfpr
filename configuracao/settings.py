import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def ler_booleano(nome, padrao):
    return os.getenv(nome, str(padrao)).strip().lower() in ("true", "1", "sim", "yes")


def ler_lista(nome, padrao=""):
    return [valor.strip() for valor in os.getenv(nome, padrao).split(",") if valor.strip()]


CHAVE_DE_DESENVOLVIMENTO = "chave-somente-para-desenvolvimento"

SECRET_KEY = os.getenv("SECRET_KEY") or CHAVE_DE_DESENVOLVIMENTO

DEBUG = ler_booleano("DEBUG", True)

if not DEBUG and SECRET_KEY in (CHAVE_DE_DESENVOLVIMENTO, "troque-esta-chave-por-uma-aleatoria"):
    raise ImproperlyConfigured("Defina uma SECRET_KEY própria no arquivo .env antes de rodar com DEBUG=False.")

ALLOWED_HOSTS = ler_lista("ALLOWED_HOSTS", "127.0.0.1,localhost")

CSRF_TRUSTED_ORIGINS = ler_lista("CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "contas",
    "itens",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "configuracao.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "itens.contexto.reivindicacoes_pendentes",
            ],
        },
    },
]

WSGI_APPLICATION = "configuracao.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

ARMAZENAMENTO = os.getenv("ARMAZENAMENTO", "local").strip().lower()

if ARMAZENAMENTO == "s3":
    armazenamento_padrao = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": os.getenv("S3_CHAVE_ACESSO"),
            "secret_key": os.getenv("S3_CHAVE_SECRETA"),
            "bucket_name": os.getenv("S3_BUCKET"),
            "region_name": os.getenv("S3_REGIAO") or None,
            "endpoint_url": os.getenv("S3_ENDPOINT") or None,
            "custom_domain": os.getenv("S3_DOMINIO_PUBLICO") or None,
            "querystring_auth": ler_booleano("S3_URL_ASSINADA", True),
            "querystring_expire": int(os.getenv("S3_URL_VALIDADE_SEGUNDOS", "3600")),
            "signature_version": "s3v4",
            "addressing_style": "path" if os.getenv("S3_ENDPOINT") else "virtual",
            "file_overwrite": False,
            "default_acl": None,
        },
    }
    if not armazenamento_padrao["OPTIONS"]["bucket_name"]:
        raise ImproperlyConfigured("Com ARMAZENAMENTO=s3, preencha S3_BUCKET, S3_CHAVE_ACESSO e S3_CHAVE_SECRETA no .env.")
elif ARMAZENAMENTO == "local":
    armazenamento_padrao = {"BACKEND": "django.core.files.storage.FileSystemStorage"}
else:
    raise ImproperlyConfigured("ARMAZENAMENTO deve ser 'local' ou 's3'.")

STORAGES = {
    "default": armazenamento_padrao,
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

FILE_UPLOAD_PERMISSIONS = 0o644

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "contas.Usuario"

LOGIN_URL = "entrar"
LOGIN_REDIRECT_URL = "inicio"
LOGOUT_REDIRECT_URL = "inicio"

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 8
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

USAR_HTTPS = ler_booleano("USAR_HTTPS", False)

if USAR_HTTPS:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

PASTA_LOGS = BASE_DIR / "logs"
PASTA_LOGS.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "padrao": {
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{",
            "datefmt": "%d/%m/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "padrao",
        },
        "arquivo_sistema": {
            "class": "logging.FileHandler",
            "filename": PASTA_LOGS / "sistema.log",
            "formatter": "padrao",
            "encoding": "utf-8",
            "delay": True,
        },
        "arquivo_erros": {
            "class": "logging.FileHandler",
            "filename": PASTA_LOGS / "erros.log",
            "formatter": "padrao",
            "encoding": "utf-8",
            "level": "WARNING",
            "delay": True,
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console", "arquivo_erros"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "arquivo_erros"],
            "level": "WARNING",
            "propagate": False,
        },
        "contas": {
            "handlers": ["console", "arquivo_sistema", "arquivo_erros"],
            "level": "INFO",
            "propagate": False,
        },
        "itens": {
            "handlers": ["console", "arquivo_sistema", "arquivo_erros"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
