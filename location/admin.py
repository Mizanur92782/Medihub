from atexit import register

from django.contrib import admin
from location.models import District, Division

@admin.register(Division)
class DivisonAdmin(admin.ModelAdmin):
  list_display=['id','division_id','division_name_bn','division_name_eng']
  ordering=['division_id']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
  list_display=[
    'id',
    'district_id',
    'district_name_bn',
    'district_name_eng',
    'division',
    'lattitude',
    'logitude',
  ]
  list_filter=['division']
  ordering=['district_id']
  