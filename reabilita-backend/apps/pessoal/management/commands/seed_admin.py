import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Cria superusuário padrão se ainda não existir (para bootstrap Docker)."

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")

        if not password:
            self.stdout.write(self.style.WARNING(
                "DJANGO_SUPERUSER_PASSWORD não definida — superusuário não criado."
            ))
            return

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if not user.check_password(password):
                user.set_password(password)
                user.save(update_fields=["password"])
                self.stdout.write(self.style.SUCCESS(
                    f"Superusuário '{username}' já existia — senha atualizada."
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"Superusuário '{username}' já existe — nenhuma ação necessária."
                ))
            return

        User.objects.create_superuser(
            username=username,
            password=password,
            email=os.getenv("DJANGO_SUPERUSER_EMAIL", ""),
        )
        self.stdout.write(self.style.SUCCESS(
            f"Superusuário '{username}' criado com sucesso."
        ))
