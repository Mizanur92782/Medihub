from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):

    help = 'Root management command of system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Running Root Seed for System Database Population\n')

        call_command('populated_division')
        call_command('populated_district')
        call_command('populated_upozila')
        call_command('populated_union')
        call_command('populated_specialization')
        call_command('populated_qualification_hospital')
        call_command('populated_user_profile')
        call_command('populated_doctor')
        call_command('populated_blood_donor')
        call_command('populated_pharmacy')
        call_command('populated_diagnostic')
        call_command('populated_ambulance')
        call_command('populated_blog')
        call_command('populated_post')
        