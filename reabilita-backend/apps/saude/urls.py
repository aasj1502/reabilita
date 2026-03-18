from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AtendimentoViewSet,
    CargaReferenciasSaudeView,
    EvolucaoMultidisciplinarViewSet,
    HistoricoCargaReferenciasView,
)

router = DefaultRouter()
router.register("atendimentos", AtendimentoViewSet)
router.register("evolucoes", EvolucaoMultidisciplinarViewSet)

urlpatterns = [
    path("carga-referencias/", CargaReferenciasSaudeView.as_view(), name="carga-referencias"),
    path(
        "carga-referencias/historico/",
        HistoricoCargaReferenciasView.as_view(),
        name="historico-carga-referencias",
    ),
    path("", include(router.urls)),
]
