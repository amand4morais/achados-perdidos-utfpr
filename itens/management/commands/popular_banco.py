import io
import unicodedata
from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from contas.models import Usuario
from itens.models import Comentario, HistoricoStatus, Item, Reivindicacao

SENHA_PADRAO = "SenhaTeste123!"

CORES_CATEGORIA = {
    Item.Categoria.ELETRONICOS: "#cfe2f3",
    Item.Categoria.DOCUMENTOS: "#d9ead3",
    Item.Categoria.VESTUARIO: "#e4d7f0",
    Item.Categoria.OUTROS: "#fce5cd",
}

ITENS = [
    {
        "chave": "pendrive",
        "autor": "admin",
        "tipo": Item.Tipo.ENCONTRADO,
        "titulo": "Pendrive Kingston 32 GB",
        "descricao": "Pendrive preto com tampa, esquecido no computador 12. Está com uma etiqueta escrita \"TCC\".",
        "categoria": Item.Categoria.ELETRONICOS,
        "local": "Laboratório de Informática, bloco E",
        "dias_atras": 1,
        "status_final": Item.Status.EM_VERIFICACAO,
    },
    {
        "chave": "carteira",
        "autor": "admin",
        "tipo": Item.Tipo.ENCONTRADO,
        "titulo": "Carteira marrom com documentos",
        "descricao": "Carteira de couro marrom encontrada embaixo de uma mesa. Tem RG e cartão de ônibus dentro.",
        "categoria": Item.Categoria.DOCUMENTOS,
        "local": "Restaurante universitário",
        "dias_atras": 9,
        "status_final": Item.Status.DEVOLVIDO,
    },
    {
        "chave": "garrafa",
        "autor": "admin",
        "tipo": Item.Tipo.ENCONTRADO,
        "titulo": "Garrafa térmica azul",
        "descricao": "Garrafa térmica de 500 ml, azul, com alguns adesivos na lateral.",
        "categoria": Item.Categoria.OUTROS,
        "local": "Biblioteca, 2º andar",
        "dias_atras": 4,
        "status_final": Item.Status.ENCONTRADO,
    },
    {
        "chave": "moletom",
        "autor": "admin",
        "tipo": Item.Tipo.ENCONTRADO,
        "titulo": "Moletom cinza com capuz",
        "descricao": "Moletom cinza tamanho M, sem estampa na frente e com o cordão do capuz faltando.",
        "categoria": Item.Categoria.VESTUARIO,
        "local": "Ginásio de esportes",
        "dias_atras": 6,
        "status_final": Item.Status.EM_VERIFICACAO,
    },
    {
        "chave": "guarda-chuva",
        "autor": "admin",
        "tipo": Item.Tipo.ENCONTRADO,
        "titulo": "Guarda-chuva preto",
        "descricao": "Guarda-chuva preto automático, deixado no suporte da entrada. Ninguém procurou desde o semestre passado.",
        "categoria": Item.Categoria.OUTROS,
        "local": "Bloco A, térreo",
        "dias_atras": 40,
        "status_final": Item.Status.ARQUIVADO,
    },
    {
        "chave": "fone",
        "autor": "usuario",
        "tipo": Item.Tipo.PERDIDO,
        "titulo": "Fone de ouvido sem fio branco",
        "descricao": "Perdi meu fone sem fio branco, dentro do estojo de carregar. O estojo tem um arranhão na tampa.",
        "categoria": Item.Categoria.ELETRONICOS,
        "local": "Sala C-105",
        "dias_atras": 2,
        "status_final": Item.Status.PERDIDO,
    },
    {
        "chave": "carteirinha",
        "autor": "usuario",
        "tipo": Item.Tipo.PERDIDO,
        "titulo": "Carteirinha estudantil",
        "descricao": "Carteirinha da UTFPR em nome de Usuário Teste. Acho que caiu do bolso no caminho para a cantina.",
        "categoria": Item.Categoria.DOCUMENTOS,
        "local": "Entre o bloco B e a cantina",
        "dias_atras": 3,
        "status_final": Item.Status.PERDIDO,
    },
    {
        "chave": "calculadora",
        "autor": "usuario",
        "tipo": Item.Tipo.ENCONTRADO,
        "titulo": "Calculadora científica",
        "descricao": "Calculadora científica cinza encontrada depois da prova de Cálculo. Tem iniciais escritas atrás.",
        "categoria": Item.Categoria.ELETRONICOS,
        "local": "Sala D-201",
        "dias_atras": 5,
        "status_final": Item.Status.EM_VERIFICACAO,
    },
    {
        "chave": "jaqueta",
        "autor": "usuario",
        "tipo": Item.Tipo.PERDIDO,
        "titulo": "Jaqueta jeans",
        "descricao": "Jaqueta jeans azul-clara com um broche amarelo no bolso.",
        "categoria": Item.Categoria.VESTUARIO,
        "local": "Auditório central",
        "dias_atras": 12,
        "status_final": Item.Status.DEVOLVIDO,
    },
    {
        "chave": "chaves",
        "autor": "usuario",
        "tipo": Item.Tipo.PERDIDO,
        "titulo": "Molho de chaves",
        "descricao": "Três chaves presas num chaveiro amarelo em formato de estrela.",
        "categoria": Item.Categoria.OUTROS,
        "local": "Estacionamento de motos",
        "dias_atras": 0,
        "status_final": Item.Status.PERDIDO,
    },
]


FONTES_SISTEMA = ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "Helvetica.ttc"]


def carregar_fonte(tamanho):
    for nome in FONTES_SISTEMA:
        try:
            return ImageFont.truetype(nome, tamanho), True
        except OSError:
            continue
    return ImageFont.load_default(size=tamanho), False


def sem_acentos(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")


def gerar_foto(titulo, categoria_valor, categoria_rotulo):
    largura, altura = 800, 600
    imagem = Image.new("RGB", (largura, altura), CORES_CATEGORIA[categoria_valor])
    desenho = ImageDraw.Draw(imagem)
    fonte_titulo, aceita_acentos = carregar_fonte(46)
    fonte_categoria, _ = carregar_fonte(28)
    if not aceita_acentos:
        titulo = sem_acentos(titulo)
        categoria_rotulo = sem_acentos(categoria_rotulo)

    desenho.rectangle([0, altura - 70, largura, altura], fill="#ffcc00")
    desenho.text((largura / 2, altura - 35), categoria_rotulo.upper(), font=fonte_categoria, fill="#1d1d1b", anchor="mm")

    linhas, linha = [], ""
    for palavra in titulo.split():
        tentativa = f"{linha} {palavra}".strip()
        if desenho.textlength(tentativa, font=fonte_titulo) > largura - 120:
            linhas.append(linha)
            linha = palavra
        else:
            linha = tentativa
    linhas.append(linha)

    altura_linha = 60
    inicio = (altura - 70) / 2 - (len(linhas) - 1) * altura_linha / 2
    for indice, texto in enumerate(linhas):
        desenho.text((largura / 2, inicio + indice * altura_linha), texto, font=fonte_titulo, fill="#1d1d1b", anchor="mm")

    saida = io.BytesIO()
    imagem.save(saida, "JPEG", quality=85)
    return ContentFile(saida.getvalue())


class Command(BaseCommand):
    help = "Cria usuários de teste e itens de exemplo em diferentes status."

    @transaction.atomic
    def handle(self, *args, **options):
        agora = timezone.now()

        admin = self.criar_usuario("admin@utfpr.br", "Administrador UTFPR", Usuario.Perfil.ADMIN)
        usuario = self.criar_usuario("usuario@utfpr.br", "Usuário Teste", Usuario.Perfil.USUARIO)
        autores = {"admin": admin, "usuario": usuario}

        removidos = Item.objects.filter(autor__in=[admin, usuario]).count()
        for item in Item.objects.filter(autor__in=[admin, usuario]):
            item.foto.delete(save=False)
            for reivindicacao in item.reivindicacoes.all():
                if reivindicacao.imagem:
                    reivindicacao.imagem.delete(save=False)
            item.delete()

        itens = {}
        for dados in ITENS:
            autor = autores[dados["autor"]]
            criado_em = agora - timedelta(days=dados["dias_atras"], hours=len(itens))
            item = Item(
                tipo=dados["tipo"],
                titulo=dados["titulo"],
                descricao=dados["descricao"],
                categoria=dados["categoria"],
                local=dados["local"],
                autor=autor,
            )
            rotulo = Item.Categoria(dados["categoria"]).label
            item.foto.save(f"{slugify(dados['chave'])}.jpg", gerar_foto(dados["titulo"], dados["categoria"], rotulo), save=False)
            item.save()
            Item.objects.filter(pk=item.pk).update(criado_em=criado_em, atualizado_em=criado_em)
            item.refresh_from_db()
            self.registrar(item, autor, "", item.status, "Item cadastrado", criado_em)
            itens[dados["chave"]] = item

        self.alterar_status(itens["garrafa"], admin, Item.Status.ENCONTRADO, "Item conferido e guardado na secretaria", horas=20)
        self.alterar_status(itens["guarda-chuva"], admin, Item.Status.ARQUIVADO, "Sem procura há mais de 30 dias", horas=24 * 35)
        self.alterar_status(itens["jaqueta"], usuario, Item.Status.DEVOLVIDO, "Dono encontrou a jaqueta com a coordenação", horas=24 * 3)

        self.comentar(itens["pendrive"], usuario, "Acho que é meu! Tem uma pasta chamada TCC_versao_final?", horas=5)
        self.comentar(itens["pendrive"], admin, "Tem sim. Abra a reivindicação descrevendo o que mais tem nele.", horas=4)
        self.comentar(itens["fone"], admin, "Vou avisar o pessoal da limpeza do bloco C para ficar de olho.", horas=30)
        self.comentar(itens["fone"], usuario, "Obrigado! Ainda não apareceu.", horas=6)
        self.comentar(itens["carteira"], usuario, "É a minha carteira, fiquei sem o RG desde ontem.", horas=24 * 8)
        self.comentar(itens["moletom"], usuario, "Esse moletom tem um nome bordado na manga?", horas=24 * 4)
        self.comentar(itens["moletom"], admin, "Não tem nada bordado.", horas=24 * 4 - 2)
        self.comentar(itens["calculadora"], admin, "Quais são as iniciais escritas atrás?", horas=24 * 2)

        self.reivindicar(itens["pendrive"], usuario, "O pendrive tem uma pasta TCC_versao_final e fotos da formatura do meu irmão.", Reivindicacao.Situacao.PENDENTE, admin, horas=3)

        aprovada = self.reivindicar(itens["carteira"], usuario, "A carteira tem meu RG em nome de Usuário Teste e uma foto 3x4 atrás do cartão.", Reivindicacao.Situacao.APROVADA, admin, horas=24 * 8 - 1)
        self.alterar_status(itens["carteira"], admin, Item.Status.DEVOLVIDO, "Reivindicação aprovada", horas=24 * 7, momento=aprovada.analisada_em)

        self.reivindicar(itens["moletom"], usuario, "Perdi um moletom cinza no ginásio na mesma semana.", Reivindicacao.Situacao.RECUSADA, admin, horas=24 * 3)

        self.stdout.write(self.style.SUCCESS("Banco populado com sucesso."))
        if removidos:
            self.stdout.write(f"{removidos} itens de exemplo antigos foram substituídos.")
        self.stdout.write(f"Usuários: {Usuario.objects.count()} | Itens: {Item.objects.count()} | "
                          f"Comentários: {Comentario.objects.count()} | Reivindicações: {Reivindicacao.objects.count()}")
        self.stdout.write(f"Admin: admin@utfpr.br / {SENHA_PADRAO}")
        self.stdout.write(f"Usuário: usuario@utfpr.br / {SENHA_PADRAO}")

    def criar_usuario(self, email, nome, perfil):
        usuario, _ = Usuario.objects.get_or_create(email=email, defaults={"nome": nome})
        usuario.nome = nome
        usuario.perfil = perfil
        usuario.is_active = True
        usuario.is_staff = perfil == Usuario.Perfil.ADMIN
        usuario.is_superuser = perfil == Usuario.Perfil.ADMIN
        usuario.set_password(SENHA_PADRAO)
        usuario.save()
        return usuario

    def momento(self, horas):
        return timezone.now() - timedelta(hours=horas)

    def registrar(self, item, usuario, anterior, novo, observacao, momento):
        registro = HistoricoStatus.objects.create(
            item=item,
            usuario=usuario,
            status_anterior=anterior,
            status_novo=novo,
            observacao=observacao,
        )
        HistoricoStatus.objects.filter(pk=registro.pk).update(criado_em=momento)

    def alterar_status(self, item, usuario, novo, observacao, horas, momento=None):
        momento = momento or self.momento(horas)
        anterior = item.status
        item.status = novo
        item.save(update_fields=["status", "atualizado_em"])
        Item.objects.filter(pk=item.pk).update(atualizado_em=momento)
        self.registrar(item, usuario, anterior, novo, observacao, momento)

    def comentar(self, item, autor, texto, horas):
        comentario = Comentario.objects.create(item=item, autor=autor, texto=texto)
        Comentario.objects.filter(pk=comentario.pk).update(criado_em=self.momento(horas))

    def reivindicar(self, item, solicitante, prova, situacao, admin, horas):
        enviada_em = self.momento(horas)
        reivindicacao = Reivindicacao.objects.create(item=item, solicitante=solicitante, prova=prova, situacao=situacao)
        campos = {"criado_em": enviada_em}
        if situacao != Reivindicacao.Situacao.PENDENTE:
            campos["analisada_por"] = admin
            campos["analisada_em"] = enviada_em + timedelta(hours=1)
        Reivindicacao.objects.filter(pk=reivindicacao.pk).update(**campos)
        reivindicacao.refresh_from_db()
        return reivindicacao
