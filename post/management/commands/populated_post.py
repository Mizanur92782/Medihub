import json
from django.core.management.base import BaseCommand
from post.models.blood_need_mod import BloodNeedPost
from post.models.medicine_need_mod import MedicineNeedPost
from post.models.equipment_need_mod import EquipmentNeedPost
from post.models.general_post_mod import GeneralPost
from authentication.models import User
from location.models import Division, District, Upozila
from medihub import settings


class Command(BaseCommand):
    help = 'Populate all post types'

    def handle(self, *args, **kwargs):
        self._populate_blood_need()
        self._populate_medicine_need()
        self._populate_equipment_need()
        self._populate_general()

    def _get_user(self, email):
        return User.objects.filter(email=email).first()

    def _get_location(self, item):
        return {
            'division': Division.objects.filter(division_name_bn=item['division']).first(),
            'district': District.objects.filter(district_name_bn=item['district']).first(),
            'upozila': Upozila.objects.filter(upoila_name_bn=item.get('upozila')).first(),
        }

    def _load(self, filename):
        filepath = settings.BASE_DIR / 'dataset' / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _populate_blood_need(self):
        if BloodNeedPost.objects.exists():
            self.stdout.write(self.style.SUCCESS('Blood need posts already populated'))
            return
        for item in self._load('blood_need_post.json'):
            user = self._get_user(item['user'])
            if not user:
                continue
            loc = self._get_location(item)
            BloodNeedPost.objects.create(
                user=user,
                patient_name=item['patient_name'],
                patient_age=item['patient_age'],
                patient_gender=item['patient_gender'],
                blood_group=item['blood_group'],
                bags_needed=item['bags_needed'],
                division=loc['division'],
                district=loc['district'],
                upozila=loc['upozila'],
                hospital_name=item['hospital_name'],
                hospital_address=item.get('hospital_address'),
                needed_date=item['needed_date'],
                needed_time=item['needed_time'],
                contact_number=item['contact_number'],
                urgency=item['urgency'],
                description=item.get('description'),
                status=item['status'],
            )
        self.stdout.write(self.style.SUCCESS('Blood need posts populated successfully'))

    def _populate_medicine_need(self):
        if MedicineNeedPost.objects.exists():
            self.stdout.write(self.style.SUCCESS('Medicine need posts already populated'))
            return
        for item in self._load('medicine_need_post.json'):
            user = self._get_user(item['user'])
            if not user:
                continue
            loc = self._get_location(item)
            MedicineNeedPost.objects.create(
                user=user,
                medicine_name=item['medicine_name'],
                quantity=item['quantity'],
                description=item.get('description'),
                division=loc['division'],
                district=loc['district'],
                upozila=loc['upozila'],
                address=item.get('address'),
                contact_number=item['contact_number'],
                urgency=item['urgency'],
                status=item['status'],
            )
        self.stdout.write(self.style.SUCCESS('Medicine need posts populated successfully'))

    def _populate_equipment_need(self):
        if EquipmentNeedPost.objects.exists():
            self.stdout.write(self.style.SUCCESS('Equipment need posts already populated'))
            return
        for item in self._load('equipment_need_post.json'):
            user = self._get_user(item['user'])
            if not user:
                continue
            loc = self._get_location(item)
            EquipmentNeedPost.objects.create(
                user=user,
                equipment_name=item['equipment_name'],
                quantity=item['quantity'],
                condition=item['condition'],
                image=item.get('image'),
                description=item.get('description'),
                division=loc['division'],
                district=loc['district'],
                upozila=loc['upozila'],
                address=item.get('address'),
                contact_number=item['contact_number'],
                urgency=item['urgency'],
                status=item['status'],
            )
        self.stdout.write(self.style.SUCCESS('Equipment need posts populated successfully'))

    def _populate_general(self):
        if GeneralPost.objects.exists():
            self.stdout.write(self.style.SUCCESS('General posts already populated'))
            return
        for item in self._load('general_post.json'):
            user = self._get_user(item['user'])
            if not user:
                continue
            loc = self._get_location(item)
            GeneralPost.objects.create(
                user=user,
                title=item['title'],
                content=item['content'],
                image=item.get('image'),
                division=loc['division'],
                district=loc['district'],
                upozila=loc['upozila'],
                contact_number=item.get('contact_number'),
                status=item['status'],
            )
        self.stdout.write(self.style.SUCCESS('General posts populated successfully'))
