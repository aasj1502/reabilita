from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AtendimentoViewSet,
    AtendimentoReferenciasView,
    CargaReferenciasSaudeView,
    Cid10AutocompleteView,
    CidOAutocompleteView,
    EvolucaoMultidisciplinarViewSet,
    HistoricoCargaReferenciasView,
)

router = DefaultRouter()
router.register("atendimentos", AtendimentoViewSet)
router.register("evolucoes", EvolucaoMultidisciplinarViewSet)

urlpatterns = [
    path(
        "atendimentos/referencias/",
        AtendimentoReferenciasView.as_view(),
        name="atendimentos-referencias",
    ),
    path("cid10/autocomplete/", Cid10AutocompleteView.as_view(), name="cid10-autocomplete"),
    path("cido/autocomplete/", CidOAutocompleteView.as_view(), name="cido-autocomplete"),
    path("carga-referencias/", CargaReferenciasSaudeView.as_view(), name="carga-referencias"),
    path(
        "carga-referencias/historico/",
        HistoricoCargaReferenciasView.as_view(),
        name="historico-carga-referencias",
    ),
    path("", include(router.urls)),
]
