
from django.core.management.base import NoArgsCommand

from core.models import Place


class Command(NoArgsCommand):
    help = u"""Update confused states from answers"""

    def handle_noargs(self, **options):
        states = Place.objects.all()
        [ s.updateDifficulty() for s in states ]