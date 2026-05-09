from django.urls import path
from location.views import union_list

urlpatterns = [
    path('unions/', union_list, name='union-list'),
]
