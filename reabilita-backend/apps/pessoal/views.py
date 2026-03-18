from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Militar, ProfissionalSaude
from .permissions import IsAdminOrReadOnly
from .serializers import MilitarSerializer, ProfissionalSaudeSerializer


class MilitarViewSet(ModelViewSet):
    queryset = Militar.objects.all()
    serializer_class = MilitarSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class ProfissionalSaudeViewSet(ModelViewSet):
    queryset = ProfissionalSaude.objects.select_related("militar").all()
    serializer_class = ProfissionalSaudeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
