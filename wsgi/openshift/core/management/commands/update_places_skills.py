
from django.core.management.base import NoArgsCommand

from core.models import Place
from questions.models import updatePlaceDifficulty

class Command(NoArgsCommand):
    help = u"""Update confused states from answers"""

    def handle_noargs(self, **options):
        places = Place.objects.all()
        [ updatePlaceDifficulty(p) for p in places ]