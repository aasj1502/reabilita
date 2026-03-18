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


class SacMapeamento(models.Model):
    lesao = models.CharField(max_length=30, blank=True)
    parte_corpo_ossea_articular = models.CharField(max_length=120, blank=True)
    parte_corpo_muscular = models.CharField(max_length=120, blank=True)
    parte_corpo_tendinosa = models.CharField(max_length=120, blank=True)
    parte_corpo_neurologica = models.CharField(max_length=120, blank=True)
    membros_superiores = models.CharField(max_length=120, blank=True)
    coluna = models.CharField(max_length=120, blank=True)
    bacia = models.CharField(max_length=120, blank=True)
    membros_inferiores = models.CharField(max_length=120, blank=True)
    lateralidade = models.CharField(max_length=30, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)
    record_hash = models.CharField(max_length=64, blank=True, help_text="SHA-256 hash do registro para detecção de mudanças")

    class Meta:
        ordering = ["id"]
        verbose_name = "SAC Mapeamento"
        verbose_name_plural = "SAC Mapeamentos"

    def __str__(self) -> str:
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


class Atendimento(models.Model):
    data_registro = models.DateTimeField(auto_now_add=True)
    cadete = models.ForeignKey("pessoal.Militar", on_delete=models.PROTECT, related_name="atendimentos")
    medico = models.ForeignKey(
        "pessoal.ProfissionalSaude",
        on_delete=models.PROTECT,
        related_name="atendimentos_medicos",
    )
    tipo_lesao = models.CharField(max_length=20, choices=TipoLesao.choices)
    origem_lesao = models.CharField(max_length=30, choices=OrigemLesao.choices)
    estrutura_anatomica = models.CharField(max_length=120)
    lateralidade = models.CharField(max_length=20, choices=Lateralidade.choices)
    codigo_cid10 = models.CharField(max_length=10)
    codigo_cido = models.CharField(max_length=10, null=True, blank=True)
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

    def clean(self) -> None:
        errors = {}

        if getattr(self, "medico_id", None) is None:
            errors["medico"] = "Não esqueça de informar o Médico!!!"

        self._validar_lateralidade(errors)
        self._validar_consistencia_oncologica(errors)

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
