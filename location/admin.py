from django.contrib import admin
from location.models import District, Division, Upozila, Union

@admin.register(Division)
class DivisonAdmin(admin.ModelAdmin):
  list_display=['id','division_id','division_name_bn','division_name_eng']
  ordering=['division_id']
  search_fields=['division_name_eng', 'division_name_bn']


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
  search_fields=['district_name_eng', 'district_name_bn']


@admin.register(Upozila)
class UpozilaAdmin(admin.ModelAdmin):
  list_display=['id', 'upozila', 'upozila_name_eng', 'upoila_name_bn', 'district']
  list_filter=['district']
  ordering=['upozila']
  search_fields=['upozila_name_eng', 'upoila_name_bn']


@admin.register(Union)
class UnionAdmin(admin.ModelAdmin):
  list_display=['id', 'union', 'union_name_eng', 'union_name_bn', 'upozila']
  list_filter=['upozila']
  ordering=['union']
  search_fields=['union_name_eng', 'union_name_bn']