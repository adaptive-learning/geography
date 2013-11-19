
from django.core.management.base import NoArgsCommand

from core.models import Place
from questions.models import update_place_difficulty


class Command(NoArgsCommand):
    help = u"""Update confused states from answers"""

    def handle_noargs(self, **options):
        places = Place.objects.all()
        for p in places:
            update_place_difficulty(p)
            p.save()
