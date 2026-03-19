import csv
import io

from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Militar, ProfissionalSaude
from .permissions import IsAdminOrReadOnly
from .serializers import MilitarSerializer, ProfissionalSaudeSerializer

ALLOWED_CSV_FIELDS = {
    "nr_militar",
    "nome_completo",
    "sexo",
    "turma",
    "posto_graduacao",
    "arma_quadro_servico",
    "curso",
    "companhia",
    "pelotao",
    "is_instrutor",
}

REQUIRED_CSV_FIELDS = {"nr_militar", "nome_completo"}


class MilitarViewSet(ModelViewSet):
    queryset = Militar.objects.all()
    serializer_class = MilitarSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    @action(detail=False, methods=["post"], url_path="bulk-csv")
    def bulk_csv(self, request):
        uploaded_file = request.FILES.get("arquivo")
        if not uploaded_file:
            return Response(
                {"detail": "Nenhum arquivo enviado. Envie um campo 'arquivo' com o CSV."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if uploaded_file.size > 2 * 1024 * 1024:
            return Response(
                {"detail": "Arquivo muito grande. Limite: 2 MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            content = uploaded_file.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            return Response(
                {"detail": "Codificação inválida. O arquivo deve ser UTF-8."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sniffer_sample = content[:2048]
        try:
            dialect = csv.Sniffer().sniff(sniffer_sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
            dialect.delimiter = ";"

        reader = csv.DictReader(io.StringIO(content), dialect=dialect)
        if reader.fieldnames is None:
            return Response(
                {"detail": "Não foi possível ler cabeçalho do CSV."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = {h.strip() for h in reader.fieldnames}
        missing = REQUIRED_CSV_FIELDS - headers
        if missing:
            return Response(
                {"detail": f"Colunas obrigatórias ausentes: {', '.join(sorted(missing))}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        criados = []
        erros = []
        for idx, row in enumerate(reader, start=2):
            cleaned = {k.strip(): (v.strip() if v else "") for k, v in row.items() if k and k.strip() in ALLOWED_CSV_FIELDS}

            if not cleaned.get("nr_militar") or not cleaned.get("nome_completo"):
                erros.append({"linha": idx, "erro": "nr_militar e nome_completo são obrigatórios."})
                continue

            is_instrutor_raw = cleaned.get("is_instrutor", "").lower()
            cleaned["is_instrutor"] = is_instrutor_raw in {"true", "1", "sim", "yes", "verdadeiro"}

            serializer = MilitarSerializer(data=cleaned)
            if not serializer.is_valid():
                erros.append({"linha": idx, "erro": serializer.errors})
                continue

            try:
                serializer.save()
                criados.append(serializer.data)
            except IntegrityError:
                erros.append({"linha": idx, "erro": f"nr_militar '{cleaned['nr_militar']}' já cadastrado."})

        return Response(
            {
                "total_enviados": (len(criados) + len(erros)),
                "total_criados": len(criados),
                "total_erros": len(erros),
                "criados": criados,
                "erros": erros,
            },
            status=status.HTTP_201_CREATED if criados else status.HTTP_400_BAD_REQUEST,
        )


class ProfissionalSaudeViewSet(ModelViewSet):
    queryset = ProfissionalSaude.objects.select_related("militar").all()
    serializer_class = ProfissionalSaudeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
