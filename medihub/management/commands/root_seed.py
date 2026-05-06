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
