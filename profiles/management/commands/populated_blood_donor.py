import json
from django.core.management.base import BaseCommand
from authentication.models import User
from profiles.models.blood_donor_mod import BloodDonor
from location.models import Division, District, Upozila
from core.enum import RoleChoices
from medihub import settings


class Command(BaseCommand):
    help = 'Populate Blood Donor profiles'

    def handle(self, *args, **kwargs):
        if BloodDonor.objects.exists():
            self.stdout.write(self.style.SUCCESS('Blood Donor profiles already populated'))
            return

        filepath = settings.BASE_DIR / 'dataset' / 'blood_donor.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            user, _ = User.objects.get_or_create(email=item['email'])
            user.set_password(item['password'])
            user.is_blood_donor = True
            user.save()

            BloodDonor.objects.create(
                user=user,
                first_name=item['first_name'],
                last_name=item['last_name'],
                date_of_birth=item['date_of_birth'],
                gender=item['gender'],
                contact_number=item['contact_number'],
                blood_group=item['blood_group'],
                availability=item['availability'],
                last_donated=item.get('last_donated'),
                division=Division.objects.filter(division_name_bn=item['division']).first(),
                district=District.objects.filter(district_name_bn=item['district']).first(),
                upozila=Upozila.objects.filter(upoila_name_bn=item['upozila']).first(),
                address=item.get('address'),
            )

        self.stdout.write(self.style.SUCCESS('Blood Donor profiles populated successfully'))
