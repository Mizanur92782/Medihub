import json
import subprocess
from typing import Any

from django.core.management.base import BaseCommand

from location.models import District, Division
from medihub import settings


class Command(BaseCommand):
    help = 'Populate District table'

    def handle(self, *args: Any, **options: Any):
        if District.objects.exists():
            self.stdout.write(self.style.SUCCESS('District table is already populated'))
        else:
          

            filepath = settings.BASE_DIR / 'dataset' / 'district.json'

            with open(filepath, 'r') as file:
                data = json.load(file)

                divisions = {d.division_id: d for d in Division.objects.all()}

                districts = [
                    District(
                        division=divisions[int(item['division_id'])],
                        district_id=int(item['id']),
                        district_name_bn=item['bn_name'],
                        district_name_eng=item['name'],
                        lattitude=item['lat'],
                        logitude=item['lon'],
                    )
                    for item in data
                ]

                District.objects.bulk_create(districts)
                self.stdout.write(self.style.SUCCESS('District populated Successfully'))
