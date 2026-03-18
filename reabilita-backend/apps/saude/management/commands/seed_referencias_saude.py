from django.core.management.base import BaseCommand

from apps.saude.services import load_referencias_saude


class Command(BaseCommand):
    help = "Carrega referências clínicas (CID-10, CID-O e SAC) a partir dos CSVs em dados/."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Remove referências existentes antes de recarregar.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Força carga mesmo sem alteração detectada nos CSVs.",
        )

    def handle(self, *args, **options):
        resultado = load_referencias_saude(
            reset=bool(options.get("reset")),
            force=bool(options.get("force")),
        )

        status = resultado.get("status")
        if status == "SEM_ALTERACAO":
            self.stdout.write(self.style.WARNING("Nenhuma alteração detectada nos CSVs."))
        elif status == "SUCESSO":
            self.stdout.write(self.style.SUCCESS("Carga de referências concluída."))
        else:
            self.stdout.write(f"Status da carga: {status}")

        self.stdout.write(f"Histórico ID: {resultado.get('historico_id')}")
        self.stdout.write(f"Arquivos alterados: {resultado.get('arquivos_alterados')}")
        self.stdout.write(f"CID-10 carregados: {resultado['cid10_carregados']}")
        self.stdout.write(f"CID-O carregados: {resultado['cido_carregados']}")
        self.stdout.write(f"SAC carregados: {resultado['sac_carregados']}")
