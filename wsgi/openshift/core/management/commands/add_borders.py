
from core.models import Place, PlaceRelation
from django.core.management.base import BaseCommand, CommandError
import csv


class Command(BaseCommand):
    help = u"""Add new places"""

    def handle(self, *args, **options):
        if(len(args) < 1):
            raise CommandError('Not enought arguments')
        file_name = args[0]
        codes = {}
        with open('eng_world.txt', 'rb') as csvfile:
            codereader = csv.reader(csvfile, delimiter='\t', quotechar='|')
            for row in codereader:
                codes[row[1].strip()] = row[0].lower().strip()

        borders_file = open(file_name)
        borders_data = borders_file.read()
        borders_lines = borders_data.split("\n")
        self.places = Place.objects.all()
        len(self.places)
        for bl in borders_lines:
            bordering = bl.split("\t")
            if len(bordering) > 4:
                if bordering[0] != "":
                    state1 = bordering[0].upper().strip()
                state2 = bordering[4].split(":")[0].upper().strip()
                if state1 in codes and state2 in codes and state2 != '':
                    self.addBorder(codes[state1], codes[state2])
                    self.stdout.write(codes[state1] + " -> " + codes[state2])

    def addBorder(self, from_code, to_code):
        from_places = self.places.filter(code=from_code)
        to_places = self.places.filter(code=to_code)
        if len(from_places) == 1 and len(to_places) == 1:
            from_place = from_places[0]
            to_place = to_places[0]
            try:
                pr = PlaceRelation.objects.get(
                    place=from_place,
                    type=PlaceRelation.HAVE_LAND_BORDER)
            except PlaceRelation.DoesNotExist:
                pr = PlaceRelation(
                    place=from_place,
                    type=PlaceRelation.HAVE_LAND_BORDER)
                pr.save()
            pr.related_places.add(to_place)
            pr.save()
