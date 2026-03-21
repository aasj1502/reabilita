from django.core.exceptions import ValidationError
from django.db import models


class Cid10Categoria(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    classificacao = models.CharField(max_length=5, blank=True)
    descricao = models.CharField(max_length=500)
    descricao_abreviada = models.CharField(max_length=500, blank=True)
    referencia = models.CharField(max_length=120, blank=True)
    excluidos = models.TextField(blank=True)
    raw_data = models.JSONField(default=dict, blank=True)
    record_hash = models.CharField(max_length=64, blank=True, help_text="SHA-256 hash do registro para detecção de mudanças")

    class Meta:
        ordering = ["codigo"]
        verbose_name = "CID-10 Categoria"
        verbose_name_plural = "CID-10 Categorias"

    def __str__(self) -> str:
        return f"{self.codigo} - {self.descricao}"


class CidOMorfologia(models.Model):
    codigo = models.CharField(max_length=12, unique=True)
    descricao = models.CharField(max_length=500)
    referencia = models.CharField(max_length=120, blank=True)
    comportamento = models.CharField(max_length=8, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)
    record_hash = models.CharField(max_length=64, blank=True, help_text="SHA-256 hash do registro para detecção de mudanças")

    class Meta:
        ordering = ["codigo"]
        verbose_name = "CID-O Morfologia"
        verbose_name_plural = "CID-O Morfologias"

    def __str__(self) -> str:
        return f"{self.codigo} - {self.descricao}"


class SaudeReferenciaLesao(models.Model):
    """Catálogo normalizado de lesões extraído de analise_mapeamento_consolidado.csv."""

    tipo_tecido = models.CharField(max_length=30, db_index=True)
    regiao_geral = models.CharField(max_length=120, db_index=True)
    sub_regiao = models.CharField(max_length=120, db_index=True)
    item_especifico = models.CharField(max_length=255)

    class Meta:
        ordering = ["tipo_tecido", "regiao_geral", "sub_regiao", "item_especifico"]
        verbose_name = "Referência de Lesão"
        verbose_name_plural = "Referências de Lesões"
        constraints = [
            models.UniqueConstraint(
                fields=["tipo_tecido", "regiao_geral", "sub_regiao", "item_especifico"],
                name="unique_referencia_lesao",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.tipo_tecido} | {self.regiao_geral} > {self.sub_regiao} > {self.item_especifico}"


class SacMapeamento(models.Model):
    lesao = models.CharField(max_length=30, blank=True)

    # --- Colunas legadas (DEPRECATED) – serão removidas após migração completa ---
    parte_corpo_ossea_articular = models.CharField(max_length=120, blank=True)
    parte_corpo_muscular = models.CharField(max_length=120, blank=True)
    parte_corpo_tendinosa = models.CharField(max_length=120, blank=True)
    parte_corpo_neurologica = models.CharField(max_length=120, blank=True)
    membros_superiores = models.CharField(max_length=120, blank=True)
    coluna = models.CharField(max_length=120, blank=True)
    bacia = models.CharField(max_length=120, blank=True)
    membros_inferiores = models.CharField(max_length=120, blank=True)
    # --- Fim das colunas legadas ---

    referencia_lesao = models.ForeignKey(
        SaudeReferenciaLesao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sac_mapeamentos",
        help_text="Referência normalizada da lesão.",
    )
    lateralidade = models.CharField(max_length=30, blank=True)
    sub_regiao_manual = models.CharField(
        max_length=120, null=True, blank=True,
        help_text="Sub-região informada manualmente quando ausente na referência.",
    )
    item_especifico_manual = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Item específico informado manualmente quando ausente na referência.",
    )
    raw_data = models.JSONField(default=dict, blank=True)
    record_hash = models.CharField(max_length=64, blank=True, help_text="SHA-256 hash do registro para detecção de mudanças")

    class Meta:
        ordering = ["id"]
        verbose_name = "SAC Mapeamento"
        verbose_name_plural = "SAC Mapeamentos"

    def __str__(self) -> str:
        if self.referencia_lesao:
            return f"{self.lesao or 'Sem lesão'} - {self.referencia_lesao}"
        return f"{self.lesao or 'Sem lesão'} - {self.membros_superiores or self.coluna or self.bacia or self.membros_inferiores}"


class CargaStatus(models.TextChoices):
    SUCESSO = "SUCESSO", "Sucesso"
    SEM_ALTERACAO = "SEM_ALTERACAO", "Sem alteração"
    FALHA = "FALHA", "Falha"


class ReferenciaArquivoVersao(models.Model):
    nome_arquivo = models.CharField(max_length=120, unique=True)
    checksum_sha256 = models.CharField(max_length=64)
    versao = models.PositiveIntegerField(default=1)
    total_registros = models.PositiveIntegerField(default=0)
    primeira_carga_em = models.DateTimeField(auto_now_add=True)
    ultima_carga_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome_arquivo"]
        verbose_name = "Versão de Arquivo de Referência"
        verbose_name_plural = "Versões de Arquivos de Referência"

    def __str__(self) -> str:
        return f"{self.nome_arquivo} v{self.versao}"


class CargaReferenciaHistorico(models.Model):
    status = models.CharField(max_length=20, choices=CargaStatus.choices)
    reset = models.BooleanField(default=False)
    force = models.BooleanField(default=False)
    arquivos_processados = models.JSONField(default=list, blank=True)
    arquivos_alterados = models.JSONField(default=list, blank=True)
    resumo = models.JSONField(default=dict, blank=True)
    mensagem = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Histórico de Carga de Referências"
        verbose_name_plural = "Histórico de Cargas de Referências"

    def __str__(self) -> str:
        return f"Carga {self.id} - {self.status}"


class TipoLesao(models.TextChoices):
    OSSEA = "Óssea", "Óssea"
    ARTICULAR = "Articular", "Articular"
    MUSCULAR = "Muscular", "Muscular"
    TENDINOSA = "Tendinosa", "Tendinosa"
    NEUROLOGICA = "Neurológica", "Neurológica"


class OrigemLesao(models.TextChoices):
    POR_ESTRESSE = "Por Estresse", "Por Estresse"
    TRAUMATICA = "Traumática", "Traumática"
    OUTRA = "Outra", "Outra"


class Lateralidade(models.TextChoices):
    DIREITA = "Direita", "Direita"
    ESQUERDA = "Esquerda", "Esquerda"
    BILATERAL = "Bilateral", "Bilateral"
    NAO_E_O_CASO = "Não é o caso", "Não é o caso"


class TipoAtendimento(models.TextChoices):
    INICIAL = "Inicial", "Inicial"
    RETORNO = "Retorno", "Retorno"


class DecisaoSred(models.TextChoices):
    INVESTIGACAO_PENDENTE = "Investigação Pendente", "Investigação Pendente"
    EM_INVESTIGACAO = "Em Investigação", "Em Investigação"
    POSITIVO = "S-RED Positivo", "S-RED Positivo"
    NEGATIVO = "S-RED Negativo", "S-RED Negativo"


# Estados terminais de S-RED (não podem ser reabertos)
DECISAO_SRED_TERMINAIS = {DecisaoSred.POSITIVO, DecisaoSred.NEGATIVO}


class Atendimento(models.Model):
    data_registro = models.DateTimeField(auto_now_add=True)
    cadete = models.ForeignKey("pessoal.Militar", on_delete=models.PROTECT, related_name="atendimentos")
    medico = models.ForeignKey(
        "pessoal.ProfissionalSaude",
        on_delete=models.PROTECT,
        related_name="atendimentos_medicos",
    )
    atendimento_origem = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="retornos",
        help_text="Atendimento inicial que originou este retorno.",
    )
    tipo_atendimento = models.CharField(
        max_length=20,
        choices=TipoAtendimento.choices,
        default=TipoAtendimento.INICIAL,
    )
    tipo_lesao = models.CharField(max_length=20, choices=TipoLesao.choices)
    origem_lesao = models.CharField(max_length=30, choices=OrigemLesao.choices, blank=True, default="")
    segmento_corporal = models.CharField(max_length=120, blank=True)
    estrutura_anatomica = models.CharField(max_length=120, blank=True)
    localizacao_lesao = models.CharField(max_length=255, blank=True)
    lateralidade = models.CharField(max_length=20, choices=Lateralidade.choices)
    referencia_lesao = models.ForeignKey(
        SaudeReferenciaLesao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="atendimentos",
        help_text="Referência normalizada da lesão (preenchida automaticamente ao salvar).",
    )
    classificacao_atividade = models.CharField(max_length=120, blank=True)
    tipo_atividade = models.CharField(max_length=120, blank=True)
    tfm_taf = models.CharField(max_length=120, blank=True)
    modalidade_esportiva = models.CharField(max_length=120, blank=True)
    conduta_terapeutica = models.CharField(max_length=120, blank=True)
    decisao_sred = models.CharField(max_length=30, choices=DecisaoSred.choices, blank=True, default="")
    medicamentoso = models.BooleanField(default=False, help_text="Tratamento medicamentoso prescrito.")
    solicitar_exames_complementares = models.BooleanField(default=False)
    exames_complementares = models.JSONField(default=list, blank=True)
    encaminhamentos_multidisciplinares = models.JSONField(default=list, blank=True)
    disposicao_cadete = models.JSONField(default=list, blank=True)
    codigo_cid10 = models.CharField(max_length=10, blank=True, default="")
    cid10_secundarios = models.JSONField(default=list, blank=True)
    codigo_cido = models.CharField(max_length=10, null=True, blank=True)
    notas_clinicas = models.TextField(blank=True)
    flag_sred = models.BooleanField(default=False, editable=False)

    class Meta:
        ordering = ["-data_registro"]

    def _deve_ativar_sred(self) -> bool:
        if self.tipo_lesao == TipoLesao.OSSEA and self.origem_lesao == OrigemLesao.POR_ESTRESSE:
            return True
        cid10_normalizado = (self.codigo_cid10 or "").upper().strip()
        return cid10_normalizado.startswith("M84.3")

    def _validar_lateralidade(self, errors: dict[str, str]) -> None:
        estrutura = (self.estrutura_anatomica or "").lower().strip()
        palavras_linha_media = {
            "coluna",
            "core",
            "tórax",
            "torax",
            "cervical",
            "torácica",
            "toracica",
            "lombar",
            "sacro",
            "cóccix",
            "coccix",
        }
        eh_linha_media = any(palavra in estrutura for palavra in palavras_linha_media)

        if eh_linha_media and self.lateralidade != Lateralidade.NAO_E_O_CASO:
            errors["lateralidade"] = "Estruturas de linha média devem usar 'Não é o caso'."
            return

        if not eh_linha_media and self.lateralidade == Lateralidade.NAO_E_O_CASO:
            errors["lateralidade"] = "Membros exigem lateralidade Direita, Esquerda ou Bilateral."

    def _validar_consistencia_oncologica(self, errors: dict[str, str]) -> None:
        cido = (self.codigo_cido or "").upper().strip()
        cid10 = (self.codigo_cid10 or "").upper().strip()
        morfologias_osseas = ("M9180/3", "M9220/3", "M9250/3")

        if cido.startswith(morfologias_osseas) and not cid10.startswith(("C40", "C41")):
            errors["codigo_cid10"] = "Morfologias CID-O ósseas exigem CID-10 no intervalo C40-C41."

    def _validar_decisao_sred(self, errors: dict[str, str]) -> None:
        deve_ativar_sred = self._deve_ativar_sred()
        decisao = (self.decisao_sred or "").strip()

        if deve_ativar_sred and not decisao:
            errors["decisao_sred"] = "Informe a decisão S-RED."

        if not deve_ativar_sred and decisao:
            self.decisao_sred = ""

    def _validar_atendimento_origem(self, errors: dict[str, str]) -> None:
        if self.tipo_atendimento == TipoAtendimento.RETORNO and not self.atendimento_origem_id:
            errors["atendimento_origem"] = "Retornos devem referenciar o atendimento de origem."
        if self.tipo_atendimento == TipoAtendimento.INICIAL and self.atendimento_origem_id:
            errors["atendimento_origem"] = "Atendimento inicial não deve ter origem."

    def clean(self) -> None:
        errors = {}

        if getattr(self, "medico_id", None) is None:
            errors["medico"] = "Não esqueça de informar o Médico!!!"

        self._validar_lateralidade(errors)
        self._validar_consistencia_oncologica(errors)
        self._validar_decisao_sred(errors)
        self._validar_atendimento_origem(errors)

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.flag_sred = self._deve_ativar_sred()
        self.full_clean()
        super().save(*args, **kwargs)


class EvolucaoMultidisciplinar(models.Model):
    atendimento = models.ForeignKey(
        Atendimento,
        on_delete=models.CASCADE,
        related_name="evolucoes",
    )
    profissional = models.ForeignKey(
        "pessoal.ProfissionalSaude",
        on_delete=models.PROTECT,
        related_name="evolucoes",
    )
    parecer_tecnico = models.TextField()
    data_evolucao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_evolucao"]

    def __str__(self) -> str:
        atendimento_id = getattr(self.atendimento, "id", "-")
        profissional_id = getattr(self.profissional, "id", "-")
        return f"Evolução {atendimento_id} - {profissional_id}"


class RecordChangeAudit(models.Model):
    """Auditoria de mudanças por linha em tabelas de referência (CID-10, CID-O, SAC)."""
    
    class ChangeType(models.TextChoices):
        CREATED = "CRIADO", "Criado"
        UPDATED = "ATUALIZADO", "Atualizado"
        UNCHANGED = "INALTERADO", "Inalterado"
    
    tabela = models.CharField(max_length=50, help_text="Nome da tabela (ex: Cid10Categoria, CidOMorfologia, SacMapeamento)")
    registro_id = models.PositiveIntegerField(help_text="ID do registro alterado")
    chave_registra = models.CharField(max_length=120, help_text="Chave única (ex: codigo CID-10)")
    tipo_mudanca = models.CharField(max_length=12, choices=ChangeType.choices)
    hash_anterior = models.CharField(max_length=64, blank=True, help_text="Hash anterior (vazio se CRIADO)")
    hash_novo = models.CharField(max_length=64, help_text="Hash novo após mudança")
    dados_alterados = models.JSONField(default=dict, blank=True, help_text="Campos que mudaram {campo: [anterior, novo]}")
    criado_em = models.DateTimeField(auto_now_add=True)
    historico_carga = models.ForeignKey(
        CargaReferenciaHistorico,
        on_delete=models.CASCADE,
        related_name="record_audits",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Auditoria de Mudança de Registro"
        verbose_name_plural = "Auditorias de Mudanças de Registro"
        indexes = [
            models.Index(fields=["tabela", "registro_id"]),
            models.Index(fields=["-criado_em"]),
        ]

    def __str__(self) -> str:
        return f"{self.tabela} {self.chave_registra}: {self.tipo_mudanca}"
