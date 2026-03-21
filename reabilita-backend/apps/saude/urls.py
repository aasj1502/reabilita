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
    ImportarCSVConfirmarView,
    ImportarCSVPreviewView,
    SaudeReferenciaLesaoHierarquiaView,
    SaudeReferenciaLesaoListView,
    SaudeReferenciaLesaoLookupView,
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
    path(
        "referencia-lesao/",
        SaudeReferenciaLesaoListView.as_view(),
        name="referencia-lesao-list",
    ),
    path(
        "referencia-lesao/lookup/",
        SaudeReferenciaLesaoLookupView.as_view(),
        name="referencia-lesao-lookup",
    ),
    path(
        "referencia-lesao/hierarquia/",
        SaudeReferenciaLesaoHierarquiaView.as_view(),
        name="referencia-lesao-hierarquia",
    ),
    path("carga-referencias/", CargaReferenciasSaudeView.as_view(), name="carga-referencias"),
    path(
        "carga-referencias/historico/",
        HistoricoCargaReferenciasView.as_view(),
        name="historico-carga-referencias",
    ),
    path("importar-csv/preview/", ImportarCSVPreviewView.as_view(), name="importar-csv-preview"),
    path("importar-csv/confirmar/", ImportarCSVConfirmarView.as_view(), name="importar-csv-confirmar"),
    path("", include(router.urls)),
]
