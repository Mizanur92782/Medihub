import json
import subprocess
from typing import Any

from django.core.management.base import BaseCommand

from profiles.models.doctor_prof_mod import Specialization, SubSpecialization
from medihub import settings


class Command(BaseCommand):
    help = 'Populate Specialization table'

    def handle(self, *args: Any, **options: Any):
        if Specialization.objects.exists():
            self.stdout.write(self.style.SUCCESS('Specialization table is already populated'))
        else:
          

            filepath = settings.BASE_DIR / 'dataset' / 'specialization.json'

            with open(filepath, 'r') as file:
                data = json.load(file)

                for item in data:
                    specialization = Specialization.objects.create(
                        name_eng=item['name_eng'],
                        name_bn=item['name_bn'],
                    )
                    SubSpecialization.objects.bulk_create([
                        SubSpecialization(
                            specialization=specialization,
                            name_eng=sub['name_eng'],
                            name_bn=sub['name_bn'],
                        )
                        for sub in item['sub']
                    ])

            self.stdout.write(self.style.SUCCESS('Specialization Created Successfully'))
