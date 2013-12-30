# -*- coding: utf-8 -*-
from core.models import Place, PlaceRelation
from django.core.management.base import BaseCommand, CommandError
import re


class Command(BaseCommand):
    help = u"""Add new places"""

    def handle(self, *args, **options):
        if(len(args) < 2):
            raise CommandError(
                'Not enough arguments. Two arguments required: <slug> <displayName>')
        file_name = 'geography/static/map/{0}.svg'.format(args[0])
        map_file = open(file_name)
        map_data = map_file.read()
        map_file.close()

        codes = re.findall(r'name="[a-zA-Z ]*"', map_data)
        codes = [c[6:-1] for c in codes]
        places = Place.objects.all()
        new_place = self.find_place_or_create_new(args[0], args[1])
        relation = PlaceRelation(place=new_place, type=PlaceRelation.IS_ON_MAP)
        relation.save()
        for p in places:
            if p.code in codes:
                relation.related_places.add(p)
        relation.save()

    def find_place_or_create_new(self, code, name):
        try:
            place = Place.objects.get(code=code)
        except Place.DoesNotExist:
            place = Place(code=code, name=name, type=Place.CONTINENT)
            place.save()
        return place
