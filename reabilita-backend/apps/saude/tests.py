"""
Testes automatizados para o módulo saúde.

Cobertura:
- Trava Médica: atendimento sem medico_id deve falhar.
- Gatilho S-RED: Óssea + Por Estresse → flag_sred=True, decisao_sred obrigatória.
- Lateralidade: estrutura de linha média → "Não é o caso"; membro → Direita/Esquerda/Bilateral.
- Consistência Oncológica: CID-O óssea obriga CID-10 C40-C41.
- Cadeia de retornos: FK atendimento_origem obrigatória para Retorno, proibida para Inicial.
- DecisaoSred granularidade: novos estados intermediários devem ser aceitos.
- Campo medicamentoso: deve funcionar como booleano.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.pessoal.models import Militar, ProfissionalSaude
from apps.saude.models import (
    Atendimento,
    DecisaoSred,
    Lateralidade,
    OrigemLesao,
    TipoAtendimento,
    TipoLesao,
)


class SaudeTestMixin:
    """Mixin para criar dados base de teste."""

    @classmethod
    def setUpTestData(cls):
        cls.militar = Militar.objects.create(
            nr_militar="TEST_001",
            nome_completo="Cadete Teste",
            sexo="M",
        )
        cls.medico_mil = Militar.objects.create(
            nr_militar="MED_TEST",
            nome_completo="Dr. Teste",
            sexo="M",
        )
        cls.medico = ProfissionalSaude.objects.create(
            militar=cls.medico_mil,
            especialidade="Médico",
            ativo=True,
        )

    def _base_attrs(self, **overrides):
        defaults = {
            "cadete": self.militar,
            "medico": self.medico,
            "tipo_atendimento": TipoAtendimento.INICIAL,
            "tipo_lesao": TipoLesao.MUSCULAR,
            "origem_lesao": OrigemLesao.TRAUMATICA,
            "segmento_corporal": "membros inferiores",
            "estrutura_anatomica": "Coxa",
            "localizacao_lesao": "Coxa",
            "lateralidade": Lateralidade.BILATERAL,
            "classificacao_atividade": "Não informado",
            "tipo_atividade": "Não informado",
            "tfm_taf": "Não informado",
            "modalidade_esportiva": "Não informado",
            "conduta_terapeutica": "Conservador",
            "decisao_sred": "",
            "medicamentoso": False,
        }
        defaults.update(overrides)
        return defaults


class TravaMedicaTest(SaudeTestMixin, TestCase):
    """Regra: atendimento sem medico_id deve falhar na validação."""

    def test_salvar_sem_medico_falha(self):
        attrs = self._base_attrs()
        attrs.pop("medico")
        atendimento = Atendimento(**attrs)
        atendimento.medico_id = None
        with self.assertRaises(ValidationError) as ctx:
            atendimento.full_clean()
        self.assertIn("medico", ctx.exception.message_dict)

    def test_salvar_com_medico_sucesso(self):
        atendimento = Atendimento(**self._base_attrs())
        atendimento.full_clean()
        atendimento.save()
        self.assertIsNotNone(atendimento.pk)


class GatilhoSredTest(SaudeTestMixin, TestCase):
    """Regra: Óssea + Por Estresse (ou CID-10 M84.3) → flag_sred=True, exige decisao_sred."""

    def test_ossea_estresse_sem_decisao_falha(self):
        atendimento = Atendimento(**self._base_attrs(
            tipo_lesao=TipoLesao.OSSEA,
            origem_lesao=OrigemLesao.POR_ESTRESSE,
            segmento_corporal="membros inferiores",
            estrutura_anatomica="Tíbia",
            localizacao_lesao="Tíbia",
            decisao_sred="",
        ))
        with self.assertRaises(ValidationError) as ctx:
            atendimento.full_clean()
        self.assertIn("decisao_sred", ctx.exception.message_dict)

    def test_ossea_estresse_com_decisao_sucesso(self):
        atendimento = Atendimento(**self._base_attrs(
            tipo_lesao=TipoLesao.OSSEA,
            origem_lesao=OrigemLesao.POR_ESTRESSE,
            segmento_corporal="membros inferiores",
            estrutura_anatomica="Tíbia",
            localizacao_lesao="Tíbia",
            decisao_sred=DecisaoSred.POSITIVO,
        ))
        atendimento.full_clean()
        atendimento.save()
        self.assertTrue(atendimento.flag_sred)

    def test_cid10_m843_ativa_sred(self):
        atendimento = Atendimento(**self._base_attrs(
            tipo_lesao=TipoLesao.OSSEA,
            origem_lesao=OrigemLesao.TRAUMATICA,
            segmento_corporal="membros inferiores",
            estrutura_anatomica="Tíbia",
            localizacao_lesao="Tíbia",
            codigo_cid10="M84.3",
            decisao_sred=DecisaoSred.NEGATIVO,
        ))
        atendimento.full_clean()
        atendimento.save()
        self.assertTrue(atendimento.flag_sred)

    def test_muscular_nao_ativa_sred(self):
        atendimento = Atendimento(**self._base_attrs(
            tipo_lesao=TipoLesao.MUSCULAR,
            origem_lesao=OrigemLesao.TRAUMATICA,
        ))
        atendimento.full_clean()
        atendimento.save()
        self.assertFalse(atendimento.flag_sred)


class DecisaoSredGranularidadeTest(SaudeTestMixin, TestCase):
    """Novos estados intermediários de S-RED devem ser aceitos."""

    def test_investigacao_pendente_aceita(self):
        atendimento = Atendimento(**self._base_attrs(
            tipo_lesao=TipoLesao.OSSEA,
            origem_lesao=OrigemLesao.POR_ESTRESSE,
            segmento_corporal="membros inferiores",
            estrutura_anatomica="Tíbia",
            localizacao_lesao="Tíbia",
            decisao_sred=DecisaoSred.INVESTIGACAO_PENDENTE,
        ))
        atendimento.full_clean()
        atendimento.save()
        self.assertEqual(atendimento.decisao_sred, "Investigação Pendente")

    def test_em_investigacao_aceita(self):
        atendimento = Atendimento(**self._base_attrs(
            tipo_lesao=TipoLesao.OSSEA,
            origem_lesao=OrigemLesao.POR_ESTRESSE,
            segmento_corporal="membros inferiores",
            estrutura_anatomica="Tíbia",
            localizacao_lesao="Tíbia",
            decisao_sred=DecisaoSred.EM_INVESTIGACAO,
        ))
        atendimento.full_clean()
        atendimento.save()
        self.assertEqual(atendimento.decisao_sred, "Em Investigação")


class LateralidadeTest(SaudeTestMixin, TestCase):
    """Regra: estrutura de linha média → 'Não é o caso'; membro → Direita/Esquerda/Bilateral."""

    def test_coluna_com_lateralidade_direita_falha(self):
        atendimento = Atendimento(**self._base_attrs(
            segmento_corporal="coluna",
            estrutura_anatomica="Coluna lombar",
            localizacao_lesao="Coluna lombar",
            lateralidade=Lateralidade.DIREITA,
        ))
        with self.assertRaises(ValidationError) as ctx:
            atendimento.full_clean()
        self.assertIn("lateralidade", ctx.exception.message_dict)

    def test_coluna_com_nao_e_o_caso_sucesso(self):
        atendimento = Atendimento(**self._base_attrs(
            segmento_corporal="coluna",
            estrutura_anatomica="Coluna lombar",
            localizacao_lesao="Coluna lombar",
            lateralidade=Lateralidade.NAO_E_O_CASO,
        ))
        atendimento.full_clean()
        atendimento.save()
        self.assertEqual(atendimento.lateralidade, "Não é o caso")

    def test_membro_com_nao_e_o_caso_falha(self):
        atendimento = Atendimento(**self._base_attrs(
            segmento_corporal="membros inferiores",
            estrutura_anatomica="Joelho",
            localizacao_lesao="Joelho",
            lateralidade=Lateralidade.NAO_E_O_CASO,
        ))
        with self.assertRaises(ValidationError) as ctx:
            atendimento.full_clean()
        self.assertIn("lateralidade", ctx.exception.message_dict)


class ConsistenciaOncologicaTest(SaudeTestMixin, TestCase):
    """Regra: CID-O óssea (M9180/3) exige CID-10 C40-C41."""

    def test_cido_ossea_sem_cid10_compativel_falha(self):
        atendimento = Atendimento(**self._base_attrs(
            tipo_lesao=TipoLesao.OSSEA,
            origem_lesao=OrigemLesao.TRAUMATICA,
            segmento_corporal="membros inferiores",
            estrutura_anatomica="Fêmur",
            localizacao_lesao="Fêmur",
            codigo_cido="M9180/3",
            codigo_cid10="S72.0",
        ))
        with self.assertRaises(ValidationError) as ctx:
            atendimento.full_clean()
        self.assertIn("codigo_cid10", ctx.exception.message_dict)

    def test_cido_ossea_com_cid10_c40_sucesso(self):
        atendimento = Atendimento(**self._base_attrs(
            tipo_lesao=TipoLesao.OSSEA,
            origem_lesao=OrigemLesao.TRAUMATICA,
            segmento_corporal="membros inferiores",
            estrutura_anatomica="Fêmur",
            localizacao_lesao="Fêmur",
            codigo_cido="M9180/3",
            codigo_cid10="C40.2",
        ))
        atendimento.full_clean()
        atendimento.save()
        self.assertIsNotNone(atendimento.pk)


class CadeiaRetornosTest(SaudeTestMixin, TestCase):
    """Regra: Retorno exige atendimento_origem; Inicial não pode ter."""

    def test_retorno_sem_origem_falha(self):
        atendimento = Atendimento(**self._base_attrs(
            tipo_atendimento=TipoAtendimento.RETORNO,
        ))
        with self.assertRaises(ValidationError) as ctx:
            atendimento.full_clean()
        self.assertIn("atendimento_origem", ctx.exception.message_dict)

    def test_retorno_com_origem_sucesso(self):
        inicial = Atendimento(**self._base_attrs())
        inicial.save()

        retorno = Atendimento(**self._base_attrs(
            tipo_atendimento=TipoAtendimento.RETORNO,
            atendimento_origem=inicial,
        ))
        retorno.full_clean()
        retorno.save()
        self.assertEqual(retorno.atendimento_origem_id, inicial.pk)

    def test_inicial_com_origem_limpa(self):
        inicial = Atendimento(**self._base_attrs())
        inicial.save()

        segundo = Atendimento(**self._base_attrs(
            tipo_atendimento=TipoAtendimento.INICIAL,
            atendimento_origem=inicial,
        ))
        with self.assertRaises(ValidationError) as ctx:
            segundo.full_clean()
        self.assertIn("atendimento_origem", ctx.exception.message_dict)


class CampoMedicamentosoTest(SaudeTestMixin, TestCase):
    """Campo medicamentoso deve funcionar como booleano."""

    def test_medicamentoso_padrao_false(self):
        atendimento = Atendimento(**self._base_attrs())
        atendimento.full_clean()
        atendimento.save()
        self.assertFalse(atendimento.medicamentoso)

    def test_medicamentoso_true(self):
        atendimento = Atendimento(**self._base_attrs(medicamentoso=True))
        atendimento.full_clean()
        atendimento.save()
        self.assertTrue(atendimento.medicamentoso)
