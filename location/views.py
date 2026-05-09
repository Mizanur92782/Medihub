from django.http import JsonResponse
from location.models import Union


def union_list(request):
    unions = Union.objects.values('union', 'union_name_bn', 'union_name_eng')
    return JsonResponse({'count': unions.count(), 'unions': list(unions)})
