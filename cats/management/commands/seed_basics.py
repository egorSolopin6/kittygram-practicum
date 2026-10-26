import os
from django.core.management.base import BaseCommand
from cats.models import Achievement


class Command(BaseCommand):
    help = 'Создаёт справочник достижений при демонстрационном запуске без изменения котов и ролей.'

    def handle(self, *args, **options):
        if os.environ.get('LOAD_DEMO_DATA', 'false') != 'true':
            return
        for name, description in [
            ('Знает команду ко мне', 'Приходит по зову хозяина.'),
            ('Ловит игрушечную мышь', 'Уверенно ловит и приносит игрушку.'),
            ('Путешественник', 'Спокойно переносит поездки в переноске.'),
        ]:
            Achievement.objects.get_or_create(name=name, defaults={'description': description})
        self.stdout.write('Справочник достижений готов.')
