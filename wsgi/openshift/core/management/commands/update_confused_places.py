
from django.core.management.base import NoArgsCommand
from django.db.models import F

from questions.models import Answer, ConfusedPlaces


class Command(NoArgsCommand):
    help = u"""Update confused states from answers"""

    def handle_noargs(self, **options):
        ConfusedPlaces.objects.all().delete()
        for a in Answer.objects.exclude(place=F("answer")):
            ConfusedPlaces.objects.was_confused(a.place, a.answer)
