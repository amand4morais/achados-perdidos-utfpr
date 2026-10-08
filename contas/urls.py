from django.urls import path

from . import views

urlpatterns = [
    path("entrar/", views.EntrarView.as_view(), name="entrar"),
    path("cadastrar/", views.CadastrarView.as_view(), name="cadastrar"),
    path("sair/", views.SairView.as_view(), name="sair"),
]
