from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    FormularioComentario,
    FormularioEdicaoItem,
    FormularioFiltro,
    FormularioItem,
    FormularioReivindicacao,
    FormularioStatus,
)
from .models import Comentario, Item, Reivindicacao

ITENS_POR_PAGINA = 12


def inicio(request):
    itens = Item.objects.select_related("autor")
    filtro = FormularioFiltro(request.GET or None)
    if filtro.is_valid():
        if filtro.cleaned_data["categoria"]:
            itens = itens.filter(categoria=filtro.cleaned_data["categoria"])
        if filtro.cleaned_data["status"]:
            itens = itens.filter(status=filtro.cleaned_data["status"])
    filtrando = filtro.is_bound and filtro.is_valid() and any(filtro.cleaned_data.values())

    pagina = Paginator(itens, ITENS_POR_PAGINA).get_page(request.GET.get("page"))
    return render(request, "inicio.html", {
        "pagina": pagina,
        "filtro": filtro,
        "filtrando": filtrando,
        "sistema_vazio": not pagina.object_list and not Item.objects.exists(),
    })


@login_required
def novo_registro(request):
    if request.method == "POST":
        form = FormularioItem(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                item = form.save(commit=False)
                item.autor = request.user
                item.status = Item.status_inicial_para(item.tipo)
                item.save()
                item.registrar_historico(request.user, "", "Item cadastrado")
            messages.success(request, "Registro cadastrado com sucesso.")
            return redirect("inicio")
    else:
        form = FormularioItem()
    return render(request, "itens/novo_registro.html", {"form": form})


def renderizar_detalhes(request, item, form_comentario=None, form_status=None, form_reivindicacao=None, abrir_modal=""):
    eh_admin = request.user.is_authenticated and request.user.eh_admin
    return render(request, "itens/detalhes.html", {
        "item": item,
        "pode_editar": item.pode_editar(request.user),
        "pode_marcar_devolvido": item.pode_marcar_devolvido(request.user),
        "eh_admin": eh_admin,
        "pode_reivindicar": item.pode_reivindicar(request.user),
        "minha_reivindicacao": item.reivindicacao_pendente_de(request.user),
        "reivindicacoes": item.reivindicacoes.select_related("solicitante", "analisada_por") if eh_admin else [],
        "comentarios": item.comentarios.select_related("autor"),
        "historico": item.historico.select_related("usuario"),
        "form_comentario": form_comentario or FormularioComentario(),
        "form_status": form_status or FormularioStatus(initial={"status": item.status}),
        "form_reivindicacao": form_reivindicacao or FormularioReivindicacao(),
        "abrir_modal": abrir_modal,
    })


def detalhes(request, pk):
    item = get_object_or_404(Item.objects.select_related("autor"), pk=pk)
    return renderizar_detalhes(request, item)


@login_required
@require_POST
def comentar(request, pk):
    item = get_object_or_404(Item.objects.select_related("autor"), pk=pk)
    form = FormularioComentario(request.POST)
    if not form.is_valid():
        return renderizar_detalhes(request, item, form_comentario=form, abrir_modal="modal-comentario")
    comentario = form.save(commit=False)
    comentario.item = item
    comentario.autor = request.user
    comentario.save()
    messages.success(request, "Comentário adicionado.")
    return redirect(f"{item.get_absolute_url()}#comentario-{comentario.pk}")


@login_required
@require_POST
def excluir_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    if not request.user.eh_admin:
        raise PermissionDenied("Somente administradores podem moderar comentários.")
    item = comentario.item
    comentario.delete()
    messages.success(request, "Comentário removido.")
    return redirect(f"{item.get_absolute_url()}#comentarios")


@login_required
def editar(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if not item.pode_editar(request.user):
        raise PermissionDenied("Somente o autor pode editar este item.")

    foto_antiga = item.foto.name
    foto_atual_url = item.foto.url if item.foto else ""
    if request.method == "POST":
        form = FormularioEdicaoItem(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save()
            if "foto" in form.changed_data and foto_antiga and foto_antiga != item.foto.name:
                item.foto.storage.delete(foto_antiga)
            messages.success(request, "Registro atualizado com sucesso.")
            return redirect("detalhes", pk=item.pk)
    else:
        form = FormularioEdicaoItem(instance=item)
    return render(request, "itens/editar.html", {"form": form, "item": item, "foto_atual_url": foto_atual_url})


@login_required
@require_POST
def excluir(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if not item.pode_editar(request.user):
        raise PermissionDenied("Somente o autor pode excluir este item.")
    item.delete()
    messages.success(request, "Registro excluído.")
    return redirect("inicio")


@login_required
@require_POST
def alterar_status(request, pk):
    item = get_object_or_404(Item.objects.select_related("autor"), pk=pk)
    if not request.user.eh_admin:
        raise PermissionDenied("Somente administradores podem alterar o status.")
    form = FormularioStatus(request.POST)
    if not form.is_valid():
        return renderizar_detalhes(request, item, form_status=form)
    novo_status = form.cleaned_data["status"]
    if item.alterar_status(novo_status, request.user, form.cleaned_data["observacao"]):
        messages.success(request, f"Status alterado para {item.get_status_display()}.")
    else:
        messages.info(request, "O item já estava com esse status.")
    return redirect(f"{item.get_absolute_url()}#historico")


@login_required
@require_POST
def marcar_devolvido(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if not item.pode_editar(request.user):
        raise PermissionDenied("Somente o autor pode marcar este item como devolvido.")
    if item.esta_finalizado:
        messages.info(request, "Este item já foi finalizado.")
    else:
        item.alterar_status(Item.Status.DEVOLVIDO, request.user, "Marcado como devolvido pelo autor")
        messages.success(request, "Item marcado como devolvido.")
    return redirect(item.get_absolute_url())


@login_required
@require_POST
def reivindicar(request, pk):
    item = get_object_or_404(Item.objects.select_related("autor"), pk=pk)
    form = FormularioReivindicacao(request.POST, request.FILES, item=item, usuario=request.user)
    if not form.is_valid():
        if form.non_field_errors():
            for erro in form.non_field_errors():
                messages.error(request, erro)
            return redirect(item.get_absolute_url())
        return renderizar_detalhes(request, item, form_reivindicacao=form, abrir_modal="modal-reivindicacao")
    with transaction.atomic():
        reivindicacao = form.save(commit=False)
        reivindicacao.item = item
        reivindicacao.solicitante = request.user
        reivindicacao.save()
        if item.status == Item.Status.ENCONTRADO:
            item.alterar_status(Item.Status.EM_VERIFICACAO, request.user, "Reivindicação recebida")
    messages.success(request, "Reivindicação enviada. Um administrador vai analisar a sua prova.")
    return redirect(item.get_absolute_url())


@login_required
def reivindicacoes(request):
    if not request.user.eh_admin:
        raise PermissionDenied("Somente administradores podem ver as reivindicações.")
    situacao = request.GET.get("situacao", Reivindicacao.Situacao.PENDENTE)
    lista = Reivindicacao.objects.select_related("item", "solicitante", "analisada_por")
    if situacao in Reivindicacao.Situacao.values:
        lista = lista.filter(situacao=situacao)
    else:
        situacao = ""
    pagina = Paginator(lista, 20).get_page(request.GET.get("page"))
    return render(request, "itens/reivindicacoes.html", {
        "pagina": pagina,
        "situacao": situacao,
        "situacoes": Reivindicacao.Situacao.choices,
    })


def analisar_reivindicacao(request, pk, aprovar):
    if not request.user.eh_admin:
        raise PermissionDenied("Somente administradores podem analisar reivindicações.")
    reivindicacao = get_object_or_404(Reivindicacao.objects.select_related("item", "solicitante"), pk=pk)
    if not reivindicacao.esta_pendente:
        messages.info(request, "Esta reivindicação já foi analisada.")
    elif aprovar:
        reivindicacao.aprovar(request.user)
        messages.success(request, f"Reivindicação aprovada. O item foi marcado como devolvido para {reivindicacao.solicitante.nome}.")
    else:
        reivindicacao.recusar(request.user)
        messages.success(request, "Reivindicação recusada. O item continua em verificação.")
    destino = request.POST.get("voltar_para")
    if destino == "lista":
        return redirect("reivindicacoes")
    return redirect(f"{reivindicacao.item.get_absolute_url()}#reivindicacoes")


@login_required
@require_POST
def aprovar_reivindicacao(request, pk):
    return analisar_reivindicacao(request, pk, aprovar=True)


@login_required
@require_POST
def recusar_reivindicacao(request, pk):
    return analisar_reivindicacao(request, pk, aprovar=False)
