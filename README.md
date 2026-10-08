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
git clone https://github.com/amand4morais/achados-perdidos-utfpr.git
cd achados-perdidos-utfpr
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

## Limitações

- **CORS não foi configurado.** O front é servido pelo próprio Django, sem SPA separado.
