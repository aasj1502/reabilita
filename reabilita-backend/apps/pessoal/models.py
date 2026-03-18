from django.db import models


class Militar(models.Model):
    nr_militar = models.CharField(max_length=30, unique=True)
    nome_completo = models.CharField(max_length=255)
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
