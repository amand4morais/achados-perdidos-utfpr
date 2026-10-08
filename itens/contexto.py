from .models import Reivindicacao


def reivindicacoes_pendentes(request):
    usuario = getattr(request, "user", None)
    if not usuario or not usuario.is_authenticated or not usuario.eh_admin:
        return {}
    return {"total_reivindicacoes_pendentes": Reivindicacao.objects.filter(situacao=Reivindicacao.Situacao.PENDENTE).count()}
