# -*- coding: utf-8 -*-
from geography.models import Place, PlaceRelation
from django.core.management.base import BaseCommand, CommandError
import re


class Command(BaseCommand):
    help = u"""Add new places"""

    def handle(self, *args, **options):
        if(len(args) < 2):
            raise CommandError(
                'Not enough arguments. Two arguments required: <slug> <displayName> [<PLACES_TYPE>]')
        file_name = 'geography/static/map/{0}.svg'.format(args[0])
        map_file = open(file_name)
        map_data = map_file.read()
        map_file.close()

        if len(args) > 2:
            place_type = Place.PLACE_TYPE_SLUGS[args[2]]
        codes = re.findall(r'-name="[^"]*"', map_data)
        codes = [c[7:-1] for c in codes]
        names = re.findall(r'realname="[^"]*"', map_data)
        names = [c[10:-1] for c in names]
        new_place = self.find_place_or_create_new(args[0], args[1])
        relation = self.find_place_relation_or_create_new(new_place)
        relation.save()
        for name, code in zip(names, codes):
            place = self.find_place_or_create_new(code, name, place_type)
            self.stdout.write(name + "\t" + code)
            relation.related_places.add(place)
        relation.save()

    def find_place_relation_or_create_new(self, place):
        try:
            place_relation = PlaceRelation.objects.get(place=place, type=PlaceRelation.IS_ON_MAP)
            place_relation.related_places.remove()
        except PlaceRelation.DoesNotExist:
            place_relation = PlaceRelation(place=place, type=PlaceRelation.IS_ON_MAP)
            place_relation.save()
        return place_relation

    def find_place_or_create_new(self, code, name, place_type=Place.UNKNOWN):
        try:
            place = Place.objects.get(code=code)
        except Place.DoesNotExist:
            place = Place(code=code, name=name, type=place_type)
            place.save()
        return place
