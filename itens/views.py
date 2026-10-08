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
    FormularioStatus,
)
from .models import Comentario, Item

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


def renderizar_detalhes(request, item, form_comentario=None, form_status=None, abrir_modal=""):
    return render(request, "itens/detalhes.html", {
        "item": item,
        "pode_editar": item.pode_editar(request.user),
        "pode_marcar_devolvido": item.pode_marcar_devolvido(request.user),
        "eh_admin": request.user.is_authenticated and request.user.eh_admin,
        "comentarios": item.comentarios.select_related("autor"),
        "historico": item.historico.select_related("usuario"),
        "form_comentario": form_comentario or FormularioComentario(),
        "form_status": form_status or FormularioStatus(initial={"status": item.status}),
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
