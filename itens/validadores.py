from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

TAMANHO_MAXIMO_IMAGEM = 5 * 1024 * 1024
FORMATOS_PERMITIDOS = {"JPEG", "PNG"}


def validar_imagem(arquivo):
    if getattr(arquivo, "_committed", False):
        return

    if arquivo.size > TAMANHO_MAXIMO_IMAGEM:
        raise ValidationError("A imagem deve ter no máximo 5 MB.")

    posicao = arquivo.tell() if hasattr(arquivo, "tell") else 0
    try:
        arquivo.seek(0)
        with Image.open(arquivo) as imagem:
            formato = imagem.format
            imagem.verify()
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        raise ValidationError("Envie uma imagem válida no formato JPG ou PNG.")
    finally:
        arquivo.seek(posicao)

    if formato not in FORMATOS_PERMITIDOS:
        raise ValidationError("Envie uma imagem válida no formato JPG ou PNG.")
