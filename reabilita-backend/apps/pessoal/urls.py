from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MilitarViewSet, ProfissionalSaudeViewSet

router = DefaultRouter()
router.register("militares", MilitarViewSet)
router.register("profissionais-saude", ProfissionalSaudeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
