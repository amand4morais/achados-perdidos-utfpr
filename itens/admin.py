from django.contrib import admin

from .models import Comentario, HistoricoStatus, Item, Reivindicacao


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    fields = ["autor", "texto", "criado_em"]
    readonly_fields = ["criado_em"]


class HistoricoStatusInline(admin.TabularInline):
    model = HistoricoStatus
    extra = 0
    fields = ["status_anterior", "status_novo", "usuario", "observacao", "criado_em"]
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["titulo", "tipo", "categoria", "status", "autor", "criado_em"]
    list_filter = ["tipo", "categoria", "status"]
    search_fields = ["titulo", "descricao", "local"]
    readonly_fields = ["criado_em", "atualizado_em"]
    inlines = [ComentarioInline, HistoricoStatusInline]


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ["item", "autor", "criado_em"]
    search_fields = ["texto"]


@admin.register(Reivindicacao)
class ReivindicacaoAdmin(admin.ModelAdmin):
    list_display = ["item", "solicitante", "situacao", "criado_em", "analisada_por"]
    list_filter = ["situacao"]


@admin.register(HistoricoStatus)
class HistoricoStatusAdmin(admin.ModelAdmin):
    list_display = ["item", "status_anterior", "status_novo", "usuario", "criado_em"]
    list_filter = ["status_novo"]
