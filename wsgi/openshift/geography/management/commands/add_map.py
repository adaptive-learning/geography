# -*- coding: utf-8 -*-
from geography.models import Place, PlaceRelation
from django.core.management.base import BaseCommand, CommandError
from xml.dom import minidom


class Command(BaseCommand):
    help = u"""Add new places"""

    def handle(self, *args, **options):
        if(len(args) < 2):
            raise CommandError(
                'Not enough arguments. Two arguments required:' +
                ' <slug> <displayName>')

        new_place = self.find_place_or_create_new(args[0], args[1])
        relation = self.find_place_relation_or_create_new(new_place)
        relation.save()

        file_name = 'geography/static/map/{0}.svg'.format(args[0])
        map_dom = minidom.parse(file_name)
        groups = map_dom.getElementsByTagName('g')
        for g in groups:
            paths = g.getElementsByTagName('path') + g.getElementsByTagName('circle')
            group_id = g.attributes['id'].value
            if group_id != 'bg':
                place_type = Place.PLACE_TYPE_SLUGS[group_id.upper()]
                self.stdout.write('## ' + group_id + ':')
                for path in paths:
                    code = path.attributes['data-code'].value
                    name = path.attributes['data-name'].value
                    if code.strip() == '':
                        continue
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
