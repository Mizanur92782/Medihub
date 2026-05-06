import json
import subprocess
from typing import Any

from django.core.management.base import BaseCommand

from location.models import Union, Upozila
from medihub import settings


class Command(BaseCommand):
    help = 'Populate Union table'

    def handle(self, *args: Any, **options: Any):
        if Union.objects.exists():
            self.stdout.write(self.style.SUCCESS('Union table is already populated'))
        else:
          

            filepath = settings.BASE_DIR / 'dataset' / 'union.json'
            
            with open(filepath, 'r') as file:
                data = json.load(file)

                upozillas = {u.upozila: u for u in Upozila.objects.all()}

                unions = [
                    Union(
                        union=int(item['id']),
                        upozila=upozillas[int(item['upazila_id'])],
                        union_name_bn=item['bn_name'],
                        union_name_eng=item['name'],
                    )
                    for item in data
                ]

                Union.objects.bulk_create(unions)
                self.stdout.write(self.style.SUCCESS('Union populated Successfully'))
