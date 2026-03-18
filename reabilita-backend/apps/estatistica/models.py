from django.db import models


class SnapshotEstatistico(models.Model):
    chave = models.CharField(max_length=80)
    referencia = models.CharField(max_length=20)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self) -> str:
        return f"{self.chave}:{self.referencia}"
