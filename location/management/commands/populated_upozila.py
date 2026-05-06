from location.models import District, Upozila
from django.core.management.base import BaseCommand
import subprocess
from medihub import settings
import json

class Command(BaseCommand):
    help = 'Populate Upazila table'

    def handle(self, *args, **kwargs):
      if Upozila.objects.exists():
        self.stdout.write(self.style.SUCCESS('Upazila table is already populated'))
      else:
        
        
        filepath =settings.BASE_DIR/'dataset'/'upazila.json'
        
        '''read file'''
        with open(filepath,'r') as file:
           data = json.load(file)
           
           districts = {d.district_id: d for d in District.objects.all()}
           
           upozila =[
             Upozila(
               district=districts[int(item['district_id'])],
               upozila=int(item['id']),
               upoila_name_bn=item['bn_name'],
               upozila_name_eng=item['name']
             )
             for item in data
           ]
           
           '''Bulk Objects Created'''
           Upozila.objects.bulk_create(upozila)
           self.stdout.write(self.style.SUCCESS("Upozila populated SucessFully"))
           
        