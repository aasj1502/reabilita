import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.pessoal.models import UserProfile


class Command(BaseCommand):
    help = "Cria/atualiza usuários padrão de desenvolvimento (um por perfil do sistema)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default=os.getenv("DJANGO_DEV_DEFAULT_PASSWORD", "Dev@12345"),
            help="Senha para todos os usuários de desenvolvimento.",
        )

    def handle(self, *args, **options):
        password = str(options.get("password") or "")
        if not password:
            self.stdout.write(self.style.ERROR("A senha não pode ser vazia."))
            return

        users = [
            {
                "perfil": "Administrador",
                "email": "admin.dev@reabilita.local",
                "nome": "Admin Dev",
                "is_staff": True,
                "especialidade_medica": "",
                "funcao_instrutor": "",
            },
            {
                "perfil": "Consultor",
                "email": "consultor.dev@reabilita.local",
                "nome": "Consultor Dev",
                "is_staff": False,
                "especialidade_medica": "",
                "funcao_instrutor": "",
            },
            {
                "perfil": "Educador Físico",
                "email": "educador.dev@reabilita.local",
                "nome": "Educador Dev",
                "is_staff": False,
                "especialidade_medica": "",
                "funcao_instrutor": "",
            },
            {
                "perfil": "Enfermeiro",
                "email": "enfermeiro.dev@reabilita.local",
                "nome": "Enfermeiro Dev",
                "is_staff": False,
                "especialidade_medica": "",
                "funcao_instrutor": "",
            },
            {
                "perfil": "Fisioterapeuta",
                "email": "fisioterapeuta.dev@reabilita.local",
                "nome": "Fisioterapeuta Dev",
                "is_staff": False,
                "especialidade_medica": "",
                "funcao_instrutor": "",
            },
            {
                "perfil": "Instrutor",
                "email": "instrutor.dev@reabilita.local",
                "nome": "Instrutor Dev",
                "is_staff": False,
                "especialidade_medica": "",
                "funcao_instrutor": "Comandante de Pelotão",
            },
            {
                "perfil": "Médico",
                "email": "medico.dev@reabilita.local",
                "nome": "Medico Dev",
                "is_staff": False,
                "especialidade_medica": "Ortopedista",
                "funcao_instrutor": "",
            },
            {
                "perfil": "Nutricionista",
                "email": "nutri.dev@reabilita.local",
                "nome": "Nutricionista Dev",
                "is_staff": False,
                "especialidade_medica": "",
                "funcao_instrutor": "",
            },
            {
                "perfil": "Psicopedagogo",
                "email": "psico.dev@reabilita.local",
                "nome": "Psicopedagogo Dev",
                "is_staff": False,
                "especialidade_medica": "",
                "funcao_instrutor": "",
            },
        ]

        user_model = get_user_model()

        for data in users:
            nome_partes = str(data["nome"]).strip().split(maxsplit=1)
            first_name = nome_partes[0] if nome_partes else ""
            last_name = nome_partes[1] if len(nome_partes) > 1 else ""

            user, created = user_model.objects.get_or_create(
                username=data["email"],
                defaults={
                    "email": data["email"],
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_active": True,
                    "is_staff": bool(data["is_staff"]),
                },
            )

            user.email = data["email"]
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            user.is_staff = bool(data["is_staff"])
            user.set_password(password)
            user.save()

            group, _ = Group.objects.get_or_create(name=data["perfil"])
            user.groups.clear()
            user.groups.add(group)

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.especialidade_medica = data["especialidade_medica"] if data["perfil"] == "Médico" else ""
            profile.funcao_instrutor = data["funcao_instrutor"] if data["perfil"] == "Instrutor" else ""
            profile.save()

            action = "criado" if created else "atualizado"
            self.stdout.write(self.style.SUCCESS(f"{data['perfil']}: {action} ({data['email']})"))
