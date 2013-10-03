
from django.core.management.base import BaseCommand, CommandError

from core.models import Place


class Command(BaseCommand):
    help = u"""Add new places"""

    def handle(self, *args, **options):
        if(len(args) < 1):
            raise CommandError('Not enought arguments')
        map_name = args[0]
        statesFile = open(map_name.lower() + ".txt")
        states = statesFile.read()
        # self.stdout.write(states)
        ss = states.split("\n")
        for s in ss:
            state = s.split("\t")
            if(len(state) == 2):
                name = state[1]
                code = state[0]
                p = Place(code=code, name=name, difficulty=500000)
                p.save()
                self.stdout.write(name + " added")

#     def handle(self, *args, **options):
#         if(len(args) < 1):
#             raise CommandError('Not enought arguments')
#         file_name = args[0]
#         mapFile = open(file_name)
#         map = mapFile.read()
#         mapFile.close()
#         import re
#         codes = re.findall(r'"[a-z]{2}"', map)
#         codes = [c[1:3] for c in codes]
#         places = Map.objects.get(name="World").places.all()
#         for p in places:
#             if not p.code in codes:
#                 self.stdout.write(p.code)
#                 p.delete()
