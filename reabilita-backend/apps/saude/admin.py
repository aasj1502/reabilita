from django.contrib import admin

from .models import (
    Atendimento,
    CargaReferenciaHistorico,
    Cid10Categoria,
    CidOMorfologia,
    EvolucaoMultidisciplinar,
    RecordChangeAudit,
    ReferenciaArquivoVersao,
    SacMapeamento,
)


@admin.register(Cid10Categoria)
class Cid10CategoriaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descricao", "classificacao", "referencia")
    search_fields = ("codigo", "descricao")


@admin.register(CidOMorfologia)
class CidOMorfologiaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descricao", "comportamento", "referencia")
    search_fields = ("codigo", "descricao")


@admin.register(SacMapeamento)
class SacMapeamentoAdmin(admin.ModelAdmin):
    list_display = (
        "lesao",
        "parte_corpo_ossea_articular",
        "parte_corpo_muscular",
        "parte_corpo_tendinosa",
        "parte_corpo_neurologica",
        "lateralidade",
    )
    search_fields = (
        "lesao",
        "parte_corpo_ossea_articular",
        "parte_corpo_muscular",
        "parte_corpo_tendinosa",
        "parte_corpo_neurologica",
        "membros_superiores",
        "coluna",
        "bacia",
        "membros_inferiores",
    )


@admin.register(ReferenciaArquivoVersao)
class ReferenciaArquivoVersaoAdmin(admin.ModelAdmin):
    list_display = ("nome_arquivo", "versao", "total_registros", "ultima_carga_em")
    search_fields = ("nome_arquivo",)


@admin.register(CargaReferenciaHistorico)
class CargaReferenciaHistoricoAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "reset", "force", "criado_em")
    list_filter = ("status", "reset", "force")
    readonly_fields = ("arquivos_processados", "arquivos_alterados", "resumo")


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "data_registro",
        "cadete",
        "medico",
        "tipo_lesao",
        "origem_lesao",
        "decisao_sred",
        "codigo_cid10",
        "flag_sred",
    )
    list_filter = ("tipo_lesao", "origem_lesao", "flag_sred", "lateralidade")
    search_fields = ("cadete__nome_completo", "codigo_cid10", "codigo_cido", "estrutura_anatomica")


@admin.register(EvolucaoMultidisciplinar)
class EvolucaoMultidisciplinarAdmin(admin.ModelAdmin):
    list_display = ("id", "atendimento", "profissional", "data_evolucao")
    list_filter = ("data_evolucao",)
    search_fields = ("parecer_tecnico",)


@admin.register(RecordChangeAudit)
class RecordChangeAuditAdmin(admin.ModelAdmin):
    list_display = ("tabela", "chave_registra", "tipo_mudanca", "criado_em")
    list_filter = ("tabela", "tipo_mudanca", "criado_em")
    search_fields = ("tabela", "chave_registra", "registro_id")
    readonly_fields = ("hash_anterior", "hash_novo", "dados_alterados", "criado_em")
