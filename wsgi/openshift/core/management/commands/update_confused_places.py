
from core.models import PlaceRelation
from django.core.management.base import NoArgsCommand
from django.db.models import F
from questions.models import Answer, ConfusedPlaces
from questions.utils import FindOnMapQuestionType


class Command(NoArgsCommand):
    help = u"""Update confused states from answers"""

    def handle_noargs(self, **options):
        ConfusedPlaces.objects.all().delete()
        
        for pr in PlaceRelation.objects.filter(type=PlaceRelation.HAVE_LAND_BORDER):
            for place2 in PlaceRelation.objects.get_bordering_places(pr.place):
                ConfusedPlaces.objects.was_confused(pr.place, place2)
                
        for a in Answer.objects.exclude(place=F("answer")).filter(type=FindOnMapQuestionType().id):
            ConfusedPlaces.objects.was_confused(a.place, a.answer)
