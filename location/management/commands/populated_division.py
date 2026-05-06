from typing import Any
import json
from django.core.management.base import BaseCommand
from httpx import delete
from medihub import settings 
from location.models import Division
import subprocess


'''Populated Devision in Database'''
class Command(BaseCommand):
  help = ''' Divison Populated'''

  
  def handle(self, *args: Any, **options: Any):
    '''file path'''
    if Division.objects.exists():
      self.stdout.write(self.style.SUCCESS("Division Alreadhy exists"))
      pass
    else:
    
      
     
      
      
      filePath = settings.BASE_DIR / "dataset" / "division.json"
      with open(filePath, "r") as file:
        data = json.load(file)
        
        divisions=[
          Division(
            division_id = item['id'],
            division_name_bn = item['bn_name'],
            division_name_eng = item['name']
            
          )
          for item in data
        ]
        
        Division.objects.bulk_create(divisions)
        
        self.stdout.write(self.style.SUCCESS('Successfully Populated Division'))