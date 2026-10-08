from functools import wraps

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Item

ITENS_POR_PAGINA = 10


def resposta_json(dados, status=200):
    return JsonResponse(dados, status=status, json_dumps_params={"ensure_ascii": False})


def somente_get(funcao):
    @csrf_exempt
    @wraps(funcao)
    def interna(request, *args, **kwargs):
        if request.method != "GET":
            resposta = resposta_json({"erro": "Método não permitido. Esta API aceita apenas GET."}, status=405)
            resposta["Allow"] = "GET"
            return resposta
        return funcao(request, *args, **kwargs)
    return interna


def data_utc(valor):
    return valor.strftime("%Y-%m-%dT%H:%M:%SZ")


def serializar_item(request, item):
    return {
        "id": item.pk,
        "titulo": item.titulo,
        "descricao": item.descricao,
        "tipo": item.tipo,
        "tipo_nome": item.get_tipo_display(),
        "categoria": item.categoria,
        "categoria_nome": item.get_categoria_display(),
        "status": item.status,
        "status_nome": item.get_status_display(),
        "local": item.local,
        "foto_url": request.build_absolute_uri(item.foto.url) if item.foto else None,
        "autor": {"id": item.autor_id, "nome": item.autor.nome},
        "criado_em": data_utc(item.criado_em),
        "atualizado_em": data_utc(item.atualizado_em),
        "url": request.build_absolute_uri(item.get_absolute_url()),
    }


def serializar_comentario(comentario):
    return {
        "id": comentario.pk,
        "autor": {"id": comentario.autor_id, "nome": comentario.autor.nome},
        "texto": comentario.texto,
        "criado_em": data_utc(comentario.criado_em),
    }


def endereco_da_pagina(request, numero):
    parametros = request.GET.copy()
    parametros["page"] = numero
    return request.build_absolute_uri(f"{request.path}?{parametros.urlencode()}")


@somente_get
def lista_itens(request):
    itens = Item.objects.select_related("autor")

    status = request.GET.get("status", "").strip()
    if status:
        if status not in Item.Status.values:
            return resposta_json({"erro": "Status inválido.", "valores_aceitos": Item.Status.values}, status=400)
        itens = itens.filter(status=status)

    categoria = request.GET.get("category", "").strip()
    if categoria:
        if categoria not in Item.Categoria.values:
            return resposta_json({"erro": "Categoria inválida.", "valores_aceitos": Item.Categoria.values}, status=400)
        itens = itens.filter(categoria=categoria)

    paginador = Paginator(itens, ITENS_POR_PAGINA)
    try:
        pagina = paginador.page(request.GET.get("page") or 1)
    except PageNotAnInteger:
        return resposta_json({"erro": "O parâmetro page deve ser um número inteiro."}, status=400)
    except EmptyPage:
        return resposta_json({"erro": "Página não encontrada.", "total_paginas": paginador.num_pages}, status=404)

    return resposta_json({
        "pagina": pagina.number,
        "total_paginas": paginador.num_pages,
        "total_itens": paginador.count,
        "itens_por_pagina": ITENS_POR_PAGINA,
        "proxima": endereco_da_pagina(request, pagina.next_page_number()) if pagina.has_next() else None,
        "anterior": endereco_da_pagina(request, pagina.previous_page_number()) if pagina.has_previous() else None,
        "itens": [serializar_item(request, item) for item in pagina.object_list],
    })


@somente_get
def detalhe_item(request, pk):
    item = Item.objects.select_related("autor").filter(pk=pk).first()
    if item is None:
        return resposta_json({"erro": "Item não encontrado."}, status=404)
    dados = serializar_item(request, item)
    dados["comentarios"] = [serializar_comentario(c) for c in item.comentarios.select_related("autor")]
    return resposta_json(dados)
