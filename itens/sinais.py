from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Item, Reivindicacao


@receiver(post_delete, sender=Item)
def apagar_foto_do_item(sender, instance, **kwargs):
    if instance.foto:
        instance.foto.delete(save=False)


@receiver(post_delete, sender=Reivindicacao)
def apagar_imagem_da_reivindicacao(sender, instance, **kwargs):
    if instance.imagem:
        instance.imagem.delete(save=False)
