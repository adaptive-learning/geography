from django.core.management.base import BaseCommand, CommandError
from geography.management import MapUpdater


class Command(BaseCommand):
    help = u"""Add new places"""

    def handle(self, *args, **options):
        if(len(args) < 2):
            raise CommandError(
                'Not enough arguments. Two arguments required:' +
                ' <slug> <displayName>')
        u = MapUpdater()
        u.update_map(args[0], args[1])
