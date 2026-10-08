from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("itens/novo/", views.novo_registro, name="novo_registro"),
    path("itens/<int:pk>/", views.detalhes, name="detalhes"),
    path("itens/<int:pk>/editar/", views.editar, name="editar"),
    path("itens/<int:pk>/excluir/", views.excluir, name="excluir"),
    path("itens/<int:pk>/status/", views.alterar_status, name="alterar_status"),
    path("itens/<int:pk>/devolvido/", views.marcar_devolvido, name="marcar_devolvido"),
    path("itens/<int:pk>/comentarios/", views.comentar, name="comentar"),
    path("comentarios/<int:pk>/excluir/", views.excluir_comentario, name="excluir_comentario"),
    path("itens/<int:pk>/reivindicar/", views.reivindicar, name="reivindicar"),
    path("reivindicacoes/", views.reivindicacoes, name="reivindicacoes"),
    path("reivindicacoes/<int:pk>/aprovar/", views.aprovar_reivindicacao, name="aprovar_reivindicacao"),
    path("reivindicacoes/<int:pk>/recusar/", views.recusar_reivindicacao, name="recusar_reivindicacao"),
]
