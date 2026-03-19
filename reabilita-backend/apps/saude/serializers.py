from rest_framework import serializers

from apps.pessoal.models import Militar, ProfissionalSaude
from .models import (
    Atendimento,
    Cid10Categoria,
    CidOMorfologia,
    DecisaoSred,
    EvolucaoMultidisciplinar,
    Lateralidade,
    OrigemLesao,
    TipoLesao,
)
from .references import build_sac_reference_maps, infer_lateralidade


class CargaReferenciasSerializer(serializers.Serializer):
    reset = serializers.BooleanField(default=False)
    force = serializers.BooleanField(default=False)


class AtendimentoSerializer(serializers.ModelSerializer):
    cadete_id = serializers.PrimaryKeyRelatedField(source="cadete", queryset=Militar.objects.all())
    medico_id = serializers.PrimaryKeyRelatedField(source="medico", queryset=ProfissionalSaude.objects.all())

    @staticmethod
    def _resolve_cid10(value: str) -> str:
        termo = (value or "").strip()
        if not termo:
            return ""

        codigo = Cid10Categoria.objects.filter(codigo__iexact=termo).values_list("codigo", flat=True).first()
        if codigo:
            return str(codigo)

        codigo_por_descricao = (
            Cid10Categoria.objects.filter(descricao__iexact=termo).values_list("codigo", flat=True).first()
        )
        if codigo_por_descricao:
            return str(codigo_por_descricao)

        return ""

    @staticmethod
    def _resolve_cido(value: str) -> str:
        termo = (value or "").strip()
        if not termo:
            return ""

        codigo = CidOMorfologia.objects.filter(codigo__iexact=termo).values_list("codigo", flat=True).first()
        if codigo:
            return str(codigo)

        codigo_por_descricao = (
            CidOMorfologia.objects.filter(descricao__iexact=termo).values_list("codigo", flat=True).first()
        )
        if codigo_por_descricao:
            return str(codigo_por_descricao)

        return ""

    @staticmethod
    def _sanitize_string_list(value: object) -> list[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("Envie uma lista de valores.")

        normalized: list[str] = []
        for item in value:
            text = str(item or "").strip()
            if text:
                normalized.append(text)

        return normalized

    def validate(self, attrs):
        tipo_lesao = attrs.get("tipo_lesao") or (getattr(self.instance, "tipo_lesao", "") if self.instance else "")
        origem_lesao = attrs.get("origem_lesao") or (getattr(self.instance, "origem_lesao", "") if self.instance else "")
        segmento_corporal = (attrs.get("segmento_corporal") or "").strip()
        estrutura_anatomica = (attrs.get("estrutura_anatomica") or "").strip()
        localizacao_lesao = (attrs.get("localizacao_lesao") or "").strip()

        sac_maps = build_sac_reference_maps()
        segmentos_por_tipo_raw = sac_maps.get("segmentos_por_tipo_lesao", {})
        estruturas_por_tipo_segmento_raw = sac_maps.get("estruturas_por_tipo_segmento", {})
        lateralidade_por_estrutura_raw = sac_maps.get("lateralidade_por_estrutura", {})

        segmentos_por_tipo = segmentos_por_tipo_raw if isinstance(segmentos_por_tipo_raw, dict) else {}
        estruturas_por_tipo_segmento = (
            estruturas_por_tipo_segmento_raw if isinstance(estruturas_por_tipo_segmento_raw, dict) else {}
        )
        lateralidade_por_estrutura = (
            lateralidade_por_estrutura_raw if isinstance(lateralidade_por_estrutura_raw, dict) else {}
        )

        errors = {}

        if tipo_lesao and segmento_corporal:
            segmentos_validos = segmentos_por_tipo.get(tipo_lesao, [])
            if segmentos_validos and segmento_corporal not in segmentos_validos:
                errors["segmento_corporal"] = "Segmento corporal inválido para o tipo de lesão selecionado."

        if tipo_lesao and segmento_corporal and estrutura_anatomica:
            estruturas_validas = (
                estruturas_por_tipo_segmento.get(tipo_lesao, {}).get(segmento_corporal, [])
            )
            if estruturas_validas and estrutura_anatomica not in estruturas_validas:
                errors["estrutura_anatomica"] = "Estrutura lesionada inválida para tipo de lesão e segmento informados."

        if "localizacao_lesao" in attrs and localizacao_lesao:
            attrs["localizacao_lesao"] = localizacao_lesao
        elif "localizacao_lesao" in attrs and estrutura_anatomica:
            attrs["localizacao_lesao"] = estrutura_anatomica

        codigo_cid10_resolvido = ""
        if "codigo_cid10" in attrs:
            codigo_cid10_resolvido = self._resolve_cid10(attrs.get("codigo_cid10", ""))
            if attrs.get("codigo_cid10") and not codigo_cid10_resolvido:
                errors["codigo_cid10"] = "Código CID-10 inválido ou inexistente na base carregada."
            attrs["codigo_cid10"] = codigo_cid10_resolvido
        elif self.instance is not None:
            codigo_cid10_resolvido = str(getattr(self.instance, "codigo_cid10", "") or "")

        decisao_sred = ""
        if "decisao_sred" in attrs:
            decisao_sred = str(attrs.get("decisao_sred") or "").strip()
        elif self.instance is not None:
            decisao_sred = str(getattr(self.instance, "decisao_sred", "") or "").strip()

        escolhas_decisao_sred = {DecisaoSred.POSITIVO, DecisaoSred.NEGATIVO}
        if decisao_sred and decisao_sred not in escolhas_decisao_sred:
            errors["decisao_sred"] = "Decisão S-RED inválida."

        if "codigo_cido" in attrs:
            codigo_cido = self._resolve_cido(attrs.get("codigo_cido", "") or "")
            if attrs.get("codigo_cido") and not codigo_cido:
                errors["codigo_cido"] = "Código CID-O inválido ou inexistente na base carregada."
            attrs["codigo_cido"] = codigo_cido or None

        if "cid10_secundarios" in attrs:
            cid10_secundarios = self._sanitize_string_list(attrs.get("cid10_secundarios"))
            cid10_secundarios_resolvidos: list[str] = []
            for codigo in cid10_secundarios:
                resolved = self._resolve_cid10(codigo)
                if not resolved:
                    errors["cid10_secundarios"] = f"Código CID-10 secundário inválido: {codigo}."
                    break
                if resolved != codigo_cid10_resolvido:
                    cid10_secundarios_resolvidos.append(resolved)
            attrs["cid10_secundarios"] = cid10_secundarios_resolvidos

        gatilho_sred = (
            tipo_lesao == TipoLesao.OSSEA and origem_lesao == OrigemLesao.POR_ESTRESSE
        ) or codigo_cid10_resolvido.startswith("M84.3")

        if gatilho_sred and not decisao_sred:
            errors["decisao_sred"] = "Informe a decisão S-RED (S-RED Positivo ou S-RED Negativo)."
        elif not gatilho_sred:
            attrs["decisao_sred"] = ""
        else:
            attrs["decisao_sred"] = decisao_sred

        tipo_atividade = str(
            attrs.get("tipo_atividade")
            or (getattr(self.instance, "tipo_atividade", "") if self.instance is not None else "")
        ).strip()
        tfm_taf = str(
            attrs.get("tfm_taf")
            or (getattr(self.instance, "tfm_taf", "") if self.instance is not None else "")
        ).strip()

        if tipo_atividade.upper() == "TFM/TAF":
            attrs["tfm_taf"] = tfm_taf or "Não informado"
        else:
            attrs["tfm_taf"] = "Não informado"

        if "encaminhamentos_multidisciplinares" in attrs:
            attrs["encaminhamentos_multidisciplinares"] = self._sanitize_string_list(
                attrs.get("encaminhamentos_multidisciplinares")
            )
        if "exames_complementares" in attrs:
            attrs["exames_complementares"] = self._sanitize_string_list(attrs.get("exames_complementares"))
        if "disposicao_cadete" in attrs:
            attrs["disposicao_cadete"] = self._sanitize_string_list(attrs.get("disposicao_cadete"))

        solicitar_exames = attrs.get("solicitar_exames_complementares")
        if solicitar_exames is None and self.instance is not None:
            solicitar_exames = bool(getattr(self.instance, "solicitar_exames_complementares", False))
        if not solicitar_exames:
            attrs["exames_complementares"] = []

        lateralidade = attrs.get("lateralidade")
        if lateralidade is None and self.instance is not None:
            lateralidade = getattr(self.instance, "lateralidade", None)
        if not lateralidade and estrutura_anatomica:
            attrs["lateralidade"] = lateralidade_por_estrutura.get(
                estrutura_anatomica,
                infer_lateralidade(segmento_corporal, estrutura_anatomica, ""),
            )
            lateralidade = attrs.get("lateralidade")

        if lateralidade not in {
            Lateralidade.DIREITA,
            Lateralidade.ESQUERDA,
            Lateralidade.BILATERAL,
            Lateralidade.NAO_E_O_CASO,
        }:
            errors["lateralidade"] = "Lateralidade inválida para o atendimento."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    class Meta:
        model = Atendimento
        fields = [
            "id",
            "data_registro",
            "cadete_id",
            "medico_id",
            "tipo_atendimento",
            "tipo_lesao",
            "origem_lesao",
            "segmento_corporal",
            "estrutura_anatomica",
            "localizacao_lesao",
            "lateralidade",
            "classificacao_atividade",
            "tipo_atividade",
            "tfm_taf",
            "modalidade_esportiva",
            "conduta_terapeutica",
            "decisao_sred",
            "solicitar_exames_complementares",
            "exames_complementares",
            "encaminhamentos_multidisciplinares",
            "disposicao_cadete",
            "codigo_cid10",
            "cid10_secundarios",
            "codigo_cido",
            "notas_clinicas",
            "flag_sred",
        ]
        read_only_fields = ["id", "data_registro", "flag_sred"]


class EvolucaoMultidisciplinarSerializer(serializers.ModelSerializer):
    atendimento_id = serializers.PrimaryKeyRelatedField(source="atendimento", queryset=Atendimento.objects.all())
    profissional_id = serializers.PrimaryKeyRelatedField(source="profissional", queryset=ProfissionalSaude.objects.all())

    class Meta:
        model = EvolucaoMultidisciplinar
        fields = [
            "id",
            "atendimento_id",
            "profissional_id",
            "parecer_tecnico",
            "data_evolucao",
        ]
        read_only_fields = ["id", "data_evolucao"]
