import json
from django.core.management.base import BaseCommand
from authentication.models import User
from profiles.models.user_prof_mod import RegularUserProfile
from location.models import Division, District, Upozila
from core.enum import RoleChoices
from medihub import settings


class Command(BaseCommand):
    help = 'Populate User profiles'

    def handle(self, *args, **kwargs):
        if RegularUserProfile.objects.exists():
            self.stdout.write(self.style.SUCCESS('User profiles already populated'))
            return

        filepath = settings.BASE_DIR / 'dataset' / 'user_profile.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            user, _ = User.objects.get_or_create(email=item['email'])
            user.set_password(item['password'])
            user.save()

            RegularUserProfile.objects.create(
                user=user,
                first_name=item['first_name'],
                last_name=item['last_name'],
                date_of_birth=item['date_of_birth'],
                gender=item['gender'],
                contact_number=item['contact_number'],
                division=Division.objects.filter(division_name_bn=item['division']).first(),
                district=District.objects.filter(district_name_bn=item['district']).first(),
                upozila=Upozila.objects.filter(upoila_name_bn=item['upozila']).first(),
                address=item.get('address'),
            )

        self.stdout.write(self.style.SUCCESS('User profiles populated successfully'))
