from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("itens/novo/", views.novo_registro, name="novo_registro"),
    path("itens/<int:pk>/", views.detalhes, name="detalhes"),
    path("itens/<int:pk>/editar/", views.editar, name="editar"),
    path("itens/<int:pk>/excluir/", views.excluir, name="excluir"),
    path("itens/<int:pk>/comentarios/", views.comentar, name="comentar"),
    path("comentarios/<int:pk>/excluir/", views.excluir_comentario, name="excluir_comentario"),
]
