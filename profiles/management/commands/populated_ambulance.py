import json
from django.core.management.base import BaseCommand
from authentication.models import User
from profiles.models.ambulance_prof_mod import AmbulanceProfile
from location.models import Division, District, Upozila
from core.enum import RoleChoices
from medihub import settings


class Command(BaseCommand):
    help = 'Populate Ambulance profiles'

    def handle(self, *args, **kwargs):
        if AmbulanceProfile.objects.exists():
            self.stdout.write(self.style.SUCCESS('Ambulance profiles already populated'))
            return

        filepath = settings.BASE_DIR / 'dataset' / 'ambulance.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            user, _ = User.objects.get_or_create(email=item['email'])
            user.set_password(item['password'])
            user.save()

            AmbulanceProfile.objects.create(
                user=user,
                owner_name=item['owner_name'],
                contact_number=item['contact_number'],
                ambulance_type=item['ambulance_type'],
                vehicle_number=item['vehicle_number'],
                is_available=item['is_available'],
                division=Division.objects.filter(division_name_bn=item['division']).first(),
                district=District.objects.filter(district_name_bn=item['district']).first(),
                upozila=Upozila.objects.filter(upoila_name_bn=item['upozila']).first(),
                address=item.get('address'),
            )

        self.stdout.write(self.style.SUCCESS('Ambulance profiles populated successfully'))
