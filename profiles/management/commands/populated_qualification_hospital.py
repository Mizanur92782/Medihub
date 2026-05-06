import json
from django.core.management.base import BaseCommand
from profiles.models.doctor_prof_mod import Qualification, Hospital
from medihub import settings


class Command(BaseCommand):
    help = 'Populate Qualification and Hospital tables'

    def handle(self, *args, **kwargs):
        self._populate(Qualification, 'qualification.json', 'Qualification')
        self._populate(Hospital, 'hospital.json', 'Hospital')

    def _populate(self, model, filename, label):
        if model.objects.exists():
            self.stdout.write(self.style.SUCCESS(f'{label} already populated'))
            return

        filepath = settings.BASE_DIR / 'dataset' / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        model.objects.bulk_create([
            model(name_eng=item['name_eng'], name_bn=item['name_bn'])
            for item in data
        ])
        self.stdout.write(self.style.SUCCESS(f'{label} populated successfully'))
