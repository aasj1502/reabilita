from django.urls import path

from .views import EficaciaReabilitacaoView, PainelClinicoView, SredAnualView

urlpatterns = [
    path("sred-anual/", SredAnualView.as_view(), name="sred-anual"),
    path("eficacia-reabilitacao/", EficaciaReabilitacaoView.as_view(), name="eficacia-reabilitacao"),
    path("painel-clinico/", PainelClinicoView.as_view(), name="painel-clinico"),
]
