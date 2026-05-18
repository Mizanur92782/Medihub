import json
from django.core.management.base import BaseCommand
from authentication.models import User
from profiles.models.diagnostic_prof_mod import DiagnosticProfile
from location.models import Division, District, Upozila
from core.enum import RoleChoices
from medihub import settings


class Command(BaseCommand):
    help = 'Populate Diagnostic profiles'

    def handle(self, *args, **kwargs):
        if DiagnosticProfile.objects.exists():
            self.stdout.write(self.style.SUCCESS('Diagnostic profiles already populated'))
            return

        filepath = settings.BASE_DIR / 'dataset' / 'diagnostic.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            user, _ = User.objects.get_or_create(email=item['email'])
            user.set_password(item['password'])
            user.save()

            DiagnosticProfile.objects.create(
                user=user,
                diagnostic_name=item['diagnostic_name'],
                owner_name=item['owner_name'],
                contact_number=item['contact_number'],
                license_number=item['license_number'],
                license_validity=item['license_validity'],
                is_open=item['is_open'],
                division=Division.objects.filter(division_name_bn=item['division']).first(),
                district=District.objects.filter(district_name_bn=item['district']).first(),
                upozila=Upozila.objects.filter(upoila_name_bn=item['upozila']).first(),
                address=item.get('address'),
            )

        self.stdout.write(self.style.SUCCESS('Diagnostic profiles populated successfully'))
