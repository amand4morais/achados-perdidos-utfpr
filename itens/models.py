from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse

from .validadores import validar_imagem


class Item(models.Model):
    class Tipo(models.TextChoices):
        PERDIDO = "perdido", "Perdido"
        ENCONTRADO = "encontrado", "Encontrado"

    class Categoria(models.TextChoices):
        ELETRONICOS = "eletronicos", "Eletrônicos"
        DOCUMENTOS = "documentos", "Documentos"
        VESTUARIO = "vestuario", "Vestuário"
        OUTROS = "outros", "Outros"

    class Status(models.TextChoices):
        PERDIDO = "perdido", "Perdido"
        ENCONTRADO = "encontrado", "Encontrado"
        EM_VERIFICACAO = "em_verificacao", "Em verificação"
        DEVOLVIDO = "devolvido", "Devolvido"
        ARQUIVADO = "arquivado", "Arquivado"

    tipo = models.CharField("tipo", max_length=10, choices=Tipo.choices)
    titulo = models.CharField("título", max_length=120)
    descricao = models.TextField("descrição", max_length=2000)
    categoria = models.CharField("categoria", max_length=15, choices=Categoria.choices)
    local = models.CharField("local aproximado", max_length=200, blank=True)
    foto = models.ImageField("foto", upload_to="itens/%Y/%m/", validators=[validar_imagem])
    status = models.CharField("status", max_length=15, choices=Status.choices)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="autor",
    )
    criado_em = models.DateTimeField("cadastrado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "item"
        verbose_name_plural = "itens"
        ordering = ["-criado_em", "-id"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["categoria"]),
        ]

    def __str__(self):
        return self.titulo

    @staticmethod
    def status_inicial_para(tipo):
        if tipo == Item.Tipo.ENCONTRADO:
            return Item.Status.EM_VERIFICACAO
        return Item.Status.PERDIDO

    def save(self, *args, **kwargs):
        if self._state.adding and not self.status:
            self.status = self.status_inicial_para(self.tipo)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("detalhes", args=[self.pk])

    def registrar_historico(self, usuario, status_anterior, observacao=""):
        return HistoricoStatus.objects.create(
            item=self,
            usuario=usuario,
            status_anterior=status_anterior,
            status_novo=self.status,
            observacao=observacao,
        )

    def pode_editar(self, usuario):
        return usuario.is_authenticated and usuario.pk == self.autor_id

    @property
    def foi_encontrado(self):
        return self.tipo == self.Tipo.ENCONTRADO

    @property
    def esta_finalizado(self):
        return self.status in (self.Status.DEVOLVIDO, self.Status.ARQUIVADO)


class Comentario(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="comentarios", verbose_name="item")
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comentarios",
        verbose_name="autor",
    )
    texto = models.TextField("comentário", max_length=1000)
    criado_em = models.DateTimeField("enviado em", auto_now_add=True)

    class Meta:
        verbose_name = "comentário"
        verbose_name_plural = "comentários"
        ordering = ["criado_em", "id"]

    def __str__(self):
        return f"{self.autor} em {self.item}"


class Reivindicacao(models.Model):
    class Situacao(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        APROVADA = "aprovada", "Aprovada"
        RECUSADA = "recusada", "Recusada"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="reivindicacoes", verbose_name="item")
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reivindicacoes",
        verbose_name="solicitante",
    )
    prova = models.CharField("comprovação", max_length=500)
    imagem = models.ImageField(
        "imagem de comprovação",
        upload_to="reivindicacoes/%Y/%m/",
        validators=[validar_imagem],
        blank=True,
    )
    situacao = models.CharField("situação", max_length=10, choices=Situacao.choices, default=Situacao.PENDENTE)
    analisada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reivindicacoes_analisadas",
        verbose_name="analisada por",
    )
    analisada_em = models.DateTimeField("analisada em", null=True, blank=True)
    criado_em = models.DateTimeField("enviada em", auto_now_add=True)

    class Meta:
        verbose_name = "reivindicação"
        verbose_name_plural = "reivindicações"
        ordering = ["-criado_em", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["item", "solicitante"],
                condition=Q(situacao="pendente"),
                name="uma_reivindicacao_pendente_por_usuario",
                violation_error_message="Você já tem uma reivindicação pendente para este item.",
            ),
        ]

    def __str__(self):
        return f"{self.solicitante} reivindica {self.item}"


class HistoricoStatus(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="historico", verbose_name="item")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alteracoes_status",
        verbose_name="alterado por",
    )
    status_anterior = models.CharField("status anterior", max_length=15, choices=Item.Status.choices, blank=True)
    status_novo = models.CharField("novo status", max_length=15, choices=Item.Status.choices)
    observacao = models.CharField("observação", max_length=200, blank=True)
    criado_em = models.DateTimeField("alterado em", auto_now_add=True)

    class Meta:
        verbose_name = "histórico de status"
        verbose_name_plural = "histórico de status"
        ordering = ["criado_em", "id"]

    def __str__(self):
        return f"{self.item}: {self.get_status_novo_display()}"
