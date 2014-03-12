from django.core.management.base import BaseCommand
from geography.management import MapUpdater


class Command(BaseCommand):
    help = u"""Add new places"""

    def handle(self, *args, **options):
        u = MapUpdater()
        u.update_all_maps()
