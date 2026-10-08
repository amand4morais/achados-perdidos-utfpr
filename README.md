# Achados e Perdidos UTFPR

Sistema web para registrar itens perdidos e encontrados no campus da UTFPR. Usuários cadastram itens com foto, comentam e reivindicam itens encontrados. O administrador altera status, modera comentários e aprova ou recusa reivindicações.

**Tecnologias:** Python, Django 6.1, SQLite e Bootstrap 5 (via CDN).

## Requisitos

- Python 3.12 ou mais recente (testado no 3.13 e no 3.14)
- Git
- Internet na instalação, para baixar as dependências com o `pip`

Não é preciso instalar banco de dados nem Node.js.

## Instalação e execução (Windows, PowerShell)

```powershell
git clone https://github.com/SEU-USUARIO/achados-perdidos.git
cd achados-perdidos
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py popular_banco
python manage.py runserver
```

Acesse **http://127.0.0.1:8000**.

Se o `activate` der erro de permissão, rode uma vez o comando abaixo, confirme com `S` e tente de novo:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Linux ou macOS

```bash
git clone https://github.com/SEU-USUARIO/achados-perdidos.git
cd achados-perdidos
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py popular_banco
python manage.py runserver
```

## Dados de teste

O comando `popular_banco` cria 2 usuários e 10 itens nos 5 status, com fotos, comentários, reivindicações e histórico. Ele pode ser executado de novo para restaurar os dados de exemplo.

| Perfil | E-mail | Senha |
|---|---|---|
| Admin | admin@utfpr.br | SenhaTeste123! |
| Usuário | usuario@utfpr.br | SenhaTeste123! |

O admin também acessa o painel do Django em `/admin`.

## Roteiro de teste

1. **Criar item Perdido:** entre como `usuario@utfpr.br`, clique em **Novo Registro**, escolha **Perdido**, preencha os campos, envie uma foto JPG ou PNG e clique em **Cadastrar**. O item aparece no topo da Home com o status **Perdido**.
2. **Criar item Encontrado:** repita escolhendo **Encontrado**. O status inicial fica **Em verificação**.
3. **Filtrar:** na Home, use os filtros de **Categoria** e **Status**.
4. **Comentar:** abra qualquer item, clique no botão flutuante **Adicionar Comentário**, escreva e clique em **Salvar**.
5. **Reivindicar:** ainda como usuário, abra o item **Garrafa térmica azul** (criado pelo admin), clique em **Reivindicar**, descreva a prova (a imagem é opcional) e envie.
6. **Aprovar:** saia e entre como `admin@utfpr.br`. Clique em **Reivindicações** na barra do topo e depois em **Aprovar**. O item passa para **Devolvido**, e a mudança aparece no **Histórico de status** do item. Se clicar em **Recusar**, o item continua **Em verificação**.
7. **Alterar status:** como admin, abra qualquer item e use o painel **Administração: alterar status**.
8. **Moderar:** como admin, use o botão **Remover** em um comentário.

## Configuração (.env)

O arquivo `.env.example` já vem pronto para rodar localmente. Para produção, copie-o para `.env` e ajuste:

| Chave | Para que serve |
|---|---|
| `SECRET_KEY` | Chave secreta do Django. Obrigatória com `DEBUG=False`. Para gerar uma: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `True` em desenvolvimento e `False` em produção |
| `ALLOWED_HOSTS` | Domínios aceitos, separados por vírgula |
| `CSRF_TRUSTED_ORIGINS` | Em produção, o endereço com `https://`, por exemplo `https://achados.exemplo.com` |
| `USAR_HTTPS` | `True` em produção com HTTPS. Ativa cookies seguros, redirecionamento e HSTS |
| `ARMAZENAMENTO` | `local` ou `s3` (veja abaixo) |
| `S3_*` | Dados do bucket, usados só quando `ARMAZENAMENTO=s3` |

## Armazenamento das fotos

- **Local (padrão):** com `ARMAZENAMENTO=local`, as fotos ficam na pasta `media/`.
- **Online (produção):** com `ARMAZENAMENTO=s3`, as fotos vão para um bucket compatível com S3 (AWS S3, Supabase Storage, Cloudflare R2 ou MinIO). Preencha no `.env`:

```env
ARMAZENAMENTO=s3
S3_BUCKET=nome-do-bucket
S3_CHAVE_ACESSO=sua-chave
S3_CHAVE_SECRETA=sua-chave-secreta
S3_REGIAO=sa-east-1
S3_ENDPOINT=
```

- **`S3_ENDPOINT`:** deixe vazio para usar a AWS. Para outros serviços, informe o endpoint deles. No Supabase, por exemplo, é `https://<projeto>.supabase.co/storage/v1/s3`.
- **URLs das fotos:** por padrão são assinadas e expiram em 1 hora (`S3_URL_VALIDADE_SEGUNDOS`). Para um bucket público com domínio próprio, use `S3_URL_ASSINADA=False` e `S3_DOMINIO_PUBLICO`.

Nos dois casos, as fotos são validadas no backend: só JPG ou PNG, com até 5 MB, e o conteúdo real do arquivo é conferido.

## API (somente leitura)

**`GET /api/items?status=&category=&page=`**

Lista paginada com 10 itens por página, dos mais recentes para os mais antigos.

- **`status`:** `perdido`, `encontrado`, `em_verificacao`, `devolvido` ou `arquivado`.
- **`category`:** `eletronicos`, `documentos`, `vestuario` ou `outros`.

```
GET http://127.0.0.1:8000/api/items?status=devolvido&category=documentos
```

```json
{
  "pagina": 1,
  "total_paginas": 1,
  "total_itens": 1,
  "itens_por_pagina": 10,
  "proxima": null,
  "anterior": null,
  "itens": [
    {
      "id": 2,
      "titulo": "Carteira marrom com documentos",
      "descricao": "Carteira de couro marrom encontrada embaixo de uma mesa...",
      "tipo": "encontrado",
      "tipo_nome": "Encontrado",
      "categoria": "documentos",
      "categoria_nome": "Documentos",
      "status": "devolvido",
      "status_nome": "Devolvido",
      "local": "Restaurante universitário",
      "foto_url": "http://127.0.0.1:8000/media/itens/2026/10/carteira.jpg",
      "autor": { "id": 1, "nome": "Administrador UTFPR" },
      "criado_em": "2026-09-29T02:45:10Z",
      "atualizado_em": "2026-09-30T05:45:11Z",
      "url": "http://127.0.0.1:8000/itens/2/"
    }
  ]
}
```

**`GET /api/items/{id}`**

Retorna o item com a mesma estrutura e mais o campo `comentarios`:

```json
"comentarios": [
  {
    "id": 1,
    "autor": { "id": 2, "nome": "Usuário Teste" },
    "texto": "Acho que é meu! Tem uma pasta chamada TCC_versao_final?",
    "criado_em": "2026-10-07T22:45:11Z"
  }
]
```

As datas da API estão em UTC. Os erros também vêm em JSON:

- `400`: filtro ou página inválidos;
- `404`: item ou página inexistente;
- `405`: método diferente de GET.

## Decisões de arquitetura

- **Django com templates e Bootstrap via CDN:** sem build de front-end. Instalar é só usar o `pip`, o que reduz o risco de falhar na hora de testar.
- **SQLite:** não exige instalar nem configurar banco.
- **Autenticação nativa do Django:**
  - senha com hash PBKDF2;
  - sessão com cookie `HttpOnly` e expiração em 8 horas;
  - proteção CSRF em todos os formulários;
  - login por e-mail com um modelo de usuário próprio.
- **Regras no backend:**
  - status inicial: Encontrado vira "Em verificação" e Perdido vira "Perdido";
  - permissões de autor e admin;
  - validação de fotos;
  - limite de uma reivindicação pendente por usuário em cada item.
- **Histórico:** toda mudança de status gera um registro, inclusive as feitas pelo `/admin`.
- **Reivindicação:**
  - quando um item Encontrado recebe uma reivindicação, ele passa para "Em verificação";
  - ao aprovar uma, as outras pendentes do mesmo item são recusadas.
- **Datas:** gravadas em UTC e exibidas no horário de Brasília.
- **Segurança:**
  - os templates escapam o HTML (proteção contra XSS);
  - páginas de erro amigáveis com `DEBUG=False`;
  - logs em `logs/sistema.log` e `logs/erros.log`.

## Limitações

- **CORS não foi configurado.** O front é servido pelo próprio Django, sem SPA separado.
- **Arquivos estáticos e fotos locais só são servidos pelo Django com `DEBUG=True`.** Em produção, use `python manage.py collectstatic` com um servidor web, ou o storage S3 para as fotos.
- **Não há envio de e-mail** para avisar o usuário quando a reivindicação é analisada. O resultado aparece no próprio sistema.
