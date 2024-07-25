import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient

RATIO_DATA = {
    Ingredient: 'ingredients.csv',
}


class Command(BaseCommand):
    help = 'Команда добавляет данные в БД из csv файлов'

    def handle(self, *args, **kwargs):
        for model, file in RATIO_DATA.items():
            with open(
                f'{settings.BASE_DIR}/data/{file}',
                'r', encoding='utf-8'
            ) as csv_data:
                reader = csv.DictReader(csv_data)
                model.objects.bulk_create(model(**data) for data in reader)
            self.stdout.write(self.style.SUCCESS('Загрузка прошла успешно'))
