from django.contrib import admin

from .models import Militar, ProfissionalSaude


@admin.register(Militar)
class MilitarAdmin(admin.ModelAdmin):
    list_display = ("nr_militar", "nome_completo", "sexo", "turma", "posto_graduacao", "is_instrutor")
    search_fields = ("nr_militar", "nome_completo")


@admin.register(ProfissionalSaude)
class ProfissionalSaudeAdmin(admin.ModelAdmin):
    list_display = ("militar", "especialidade", "registro_profissional", "ativo")
    list_filter = ("especialidade", "ativo")
    search_fields = ("militar__nome_completo", "registro_profissional")
