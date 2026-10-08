from django.apps import AppConfig


class ItensConfig(AppConfig):
    name = "itens"
    verbose_name = "Itens"

    def ready(self):
        from . import sinais
