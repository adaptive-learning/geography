from django.core.management.base import BaseCommand, CommandError
from geography.models import Place


class Command(BaseCommand):
    help = u"""Add new places"""
    usage_str = 'USAGE: ./manage.py add_places map_name STATE|CITY|RIVER|LAKE|... [difficulty]'

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError(self.usage_str)
        if not args[1] in Place.PLACE_TYPE_SLUGS:
            raise CommandError(self.usage_str)
        place_type = self.Place.PLACE_TYPE_SLUGS[args[1]]
        map_name = args[0]
        state_file = open(map_name.lower() + ".txt")
        states = state_file.read()
        ss = states.split("\n")
        for s in ss:
            place = s.split("\t")
            if(len(place) == 2):
                name = place[1]
                code = place[0]
                p = Place(code=code, name=name, difficulty=500, type=place_type)
                p.save()
                self.stdout.write(name + " added")
