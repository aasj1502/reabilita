from django.conf import settings
from django.db import models


class AnoCadete(models.TextChoices):
    ANO_1 = "1º Ano", "1º Ano"
    ANO_2 = "2º Ano", "2º Ano"
    ANO_3 = "3º Ano", "3º Ano"
    ANO_4 = "4º Ano", "4º Ano"
    ANO_5 = "5º Ano", "5º Ano"


class Militar(models.Model):
    nr_militar = models.CharField(max_length=30, unique=True)
    matricula = models.CharField(
        max_length=30,
        blank=True,
        default="",
        db_index=True,
        help_text="Matrícula ou identificador alternativo para rastreabilidade anônima.",
    )
    nome_completo = models.CharField(max_length=255)
    nome_guerra = models.CharField(max_length=80, blank=True)
    sexo = models.CharField(max_length=30, blank=True)
    turma = models.CharField(max_length=40, blank=True)
    ano = models.CharField(max_length=10, choices=AnoCadete.choices, blank=True)
    posto_graduacao = models.CharField(max_length=80, blank=True)
    arma_quadro_servico = models.CharField(max_length=80, blank=True)
    curso = models.CharField(max_length=120, blank=True)
    companhia = models.CharField(max_length=80, blank=True)
    pelotao = models.CharField(max_length=80, blank=True)
    is_instrutor = models.BooleanField(default=False)

    class Meta:
        ordering = ["nome_completo"]

    def __str__(self) -> str:
        return self.nome_completo


class EspecialidadeMedica(models.TextChoices):
    ORTOPEDISTA = "Ortopedista", "Ortopedista"
    CLINICO_GERAL = "Clínico Geral", "Clínico Geral"


class FuncaoInstrutor(models.TextChoices):
    CMT_CC = "Comandante do Corpo de Cadetes", "Comandante do Corpo de Cadetes"
    SUBCMT_CC = "Subcomandante do Corpo de Cadetes", "Subcomandante do Corpo de Cadetes"
    S1_CC = "S1-CC", "S1-CC"
    CMT_CURSO = "Comandante de Curso", "Comandante de Curso"
    CMT_SU = "Comandante de Subunidade", "Comandante de Subunidade"
    CMT_PEL = "Comandante de Pelotão", "Comandante de Pelotão"


class EspecialidadeSaude(models.TextChoices):
    MEDICO = "Médico", "Médico"
    FISIOTERAPEUTA = "Fisioterapeuta", "Fisioterapeuta"
    NUTRICIONISTA = "Nutricionista", "Nutricionista"
    PSICOPEDAGOGO = "Psicopedagogo", "Psicopedagogo"
    ESTATISTICO = "Estatístico", "Estatístico"


class ProfissionalSaude(models.Model):
    militar = models.OneToOneField(Militar, on_delete=models.PROTECT, related_name="perfil_saude")
    especialidade = models.CharField(max_length=40, choices=EspecialidadeSaude.choices)
    registro_profissional = models.CharField(max_length=50, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Profissional de Saúde"
        verbose_name_plural = "Profissionais de Saúde"

    def __str__(self) -> str:
        return f"{self.militar.nome_completo} ({self.especialidade})"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    especialidade_medica = models.CharField(
        max_length=30,
        choices=EspecialidadeMedica.choices,
        blank=True,
        default="",
    )
    funcao_instrutor = models.CharField(
        max_length=60,
        choices=FuncaoInstrutor.choices,
        blank=True,
        default="",
    )
    posto_graduacao = models.CharField(max_length=80, blank=True, default="")
    nome_guerra = models.CharField(max_length=80, blank=True, default="")
    setor = models.CharField(max_length=120, blank=True, default="")
    fracao = models.CharField(max_length=120, blank=True, default="")

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self) -> str:
        return f"Profile({self.user.username})"
