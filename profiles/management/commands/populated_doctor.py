import json
from django.core.management.base import BaseCommand
from authentication.models import User
from profiles.models.doctor_prof_mod import (
    Doctor, DoctorDetails, DoctorEducation,
    DoctorWorkingExperience, DoctorScheduling,
    Specialization, SubSpecialization, Qualification, Hospital,
)
from location.models import Division, District
from core.enum import RoleChoices
from medihub import settings


class Command(BaseCommand):
    help = 'Populate Doctor profiles'

    def handle(self, *args, **kwargs):
        if Doctor.objects.exists():
            self.stdout.write(self.style.SUCCESS('Doctor profiles already populated'))
            return

        filepath = settings.BASE_DIR / 'dataset' / 'doctor.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            user, _ = User.objects.get_or_create(email=item['email'])
            user.set_password(item['password'])
            user.save()

            division = Division.objects.filter(division_name_bn=item['division']).first()
            district = District.objects.filter(district_name_bn=item['district']).first()
            specialization = Specialization.objects.filter(name_eng=item['specialization']).first()
            sub_specialization = SubSpecialization.objects.filter(name_eng=item['sub_specialization']).first()

            doctor = Doctor.objects.create(
                user=user,
                first_name=item['first_name'],
                last_name=item['last_name'],
                date_of_birth=item['date_of_birth'],
                gender=item['gender'],
                contact_number=item['contact_number'],
                division=division,
                district=district,
                specialization=specialization,
                sub_specialization=sub_specialization,
                years_of_experience=item['years_of_experience'],
                license_number=item['license_number'],
                license_validity=item['license_validity'],
            )

            qualifications = Qualification.objects.filter(name_eng__in=item['qualifications'])
            doctor.qualifications.set(qualifications)

            hospitals = Hospital.objects.filter(name_eng__in=item['hospital_affiliations'])
            doctor.hospital_affiliations.set(hospitals)

            DoctorDetails.objects.create(
                doctor=doctor,
                bio=item.get('bio'),
                language=item.get('language'),
            )

            DoctorEducation.objects.bulk_create([
                DoctorEducation(
                    doctor=doctor,
                    institution=edu['institution'],
                    degree=edu['degree'],
                    start_at=edu['start_at'],
                    end_at=edu.get('end_at'),
                )
                for edu in item.get('educations', [])
            ])

            DoctorWorkingExperience.objects.bulk_create([
                DoctorWorkingExperience(
                    doctor=doctor,
                    institution=exp['institution'],
                    position=exp['position'],
                    starting_at=exp['starting_at'],
                    end_at=exp.get('end_at'),
                )
                for exp in item.get('experiences', [])
            ])

            DoctorScheduling.objects.bulk_create([
                DoctorScheduling(
                    doctor=doctor,
                    day=sch['day'],
                    start=sch['start'],
                    end=sch['end'],
                )
                for sch in item.get('schedules', [])
            ])

        self.stdout.write(self.style.SUCCESS('Doctor profiles populated successfully'))
