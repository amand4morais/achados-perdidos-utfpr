import os

from django import forms

from contas.forms import CamposBootstrapMixin

from .models import Comentario, Item

EXTENSOES_PERMITIDAS = {".jpg", ".jpeg", ".png"}
TIPOS_PERMITIDOS = {"image/jpeg", "image/png", "image/pjpeg"}


def conferir_arquivo_imagem(arquivo):
    if not arquivo or not hasattr(arquivo, "content_type"):
        return arquivo
    extensao = os.path.splitext(arquivo.name)[1].lower()
    if extensao not in EXTENSOES_PERMITIDAS or arquivo.content_type not in TIPOS_PERMITIDOS:
        raise forms.ValidationError("Envie uma imagem no formato JPG ou PNG.")
    return arquivo


class FormularioItem(CamposBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Item
        fields = ["tipo", "titulo", "descricao", "categoria", "local", "foto"]
        widgets = {
            "tipo": forms.RadioSelect,
            "descricao": forms.Textarea(attrs={"rows": 4}),
            "local": forms.TextInput(attrs={"placeholder": "Ex.: Bloco B, sala 204"}),
            "foto": forms.FileInput(attrs={"accept": "image/jpeg,image/png"}),
        }
        help_texts = {
            "foto": "JPG ou PNG com até 5 MB.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "tipo" in self.fields:
            self.fields["tipo"].choices = list(Item.Tipo.choices)
        if "categoria" in self.fields:
            self.fields["categoria"].choices = [("", "Selecione")] + list(Item.Categoria.choices)

    def clean_titulo(self):
        return " ".join(self.cleaned_data["titulo"].split())

    def clean_descricao(self):
        return self.cleaned_data["descricao"].strip()

    def clean_local(self):
        return " ".join(self.cleaned_data.get("local", "").split())

    def clean_foto(self):
        return conferir_arquivo_imagem(self.cleaned_data.get("foto"))


class FormularioEdicaoItem(FormularioItem):
    class Meta(FormularioItem.Meta):
        fields = ["titulo", "descricao", "categoria", "local", "foto"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 4}),
            "local": forms.TextInput(attrs={"placeholder": "Ex.: Bloco B, sala 204"}),
            "foto": forms.FileInput(attrs={"accept": "image/jpeg,image/png"}),
        }
        help_texts = {
            "foto": "Envie uma nova foto só se quiser trocar a atual. JPG ou PNG com até 5 MB.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["foto"].required = False


class FormularioFiltro(forms.Form):
    categoria = forms.ChoiceField(
        required=False,
        choices=[("", "Todas")] + list(Item.Categoria.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Todos")] + list(Item.Status.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class FormularioComentario(CamposBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["texto"]
        widgets = {
            "texto": forms.Textarea(attrs={"rows": 4, "maxlength": 1000, "placeholder": "Escreva sua mensagem"}),
        }

    def clean_texto(self):
        texto = self.cleaned_data["texto"].strip()
        if not texto:
            raise forms.ValidationError("Escreva alguma coisa antes de salvar.")
        return texto
