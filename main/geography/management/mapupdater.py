# -*- coding: utf-8 -*-
from geography.models import Place, PlaceRelation
from xml.dom import minidom
from os import listdir
import settings


class MapUpdater():

    places_cache = {}

    def update_all_maps(self):
        for p in Place.objects.all():
            self.places_cache[p.code] = p

        self.find_place_or_create_new('world', 'Svět', Place.WORLD)
        self.update_map('world', 'Svět')
        continents = (
            ('europe', 'Evropa'),
            ('asia', 'Asie'),
            ('oceania', 'Austrálie a Oceánie'),
            ('samerica', 'Jižní Amerika'),
            ('namerica', 'Severní Amerika'),
            ('africa', 'Afrika'),
        )
        for c in continents:
            self.find_place_or_create_new(c[0], c[1], Place.CONTINENT)
        for f in sorted(listdir(settings.PROJECT_DIR + '/geography/static/map/')):
            if f.endswith('.svg'):
                print 'updating map: ' + f
                self.update_map(f[:-4], None)

    def update_map(self, map_code, map_name):
        new_place = self.find_place_or_create_new(map_code, map_name)
        relation = self.find_place_relation_or_create_new(new_place)

        try:
            too_small_places = PlaceRelation.objects.get(
                place__code=map_code,
                type=PlaceRelation.IS_TOO_SMALL_ON_MAP)
            too_small_places_codes = [p.code for p in too_small_places.related_places.all()]
        except PlaceRelation.DoesNotExist:
            too_small_places_codes = []

        file_name = settings.PROJECT_DIR + '/geography/static/map/{0}.svg'.format(map_code)
        map_dom = minidom.parse(file_name)
        groups = map_dom.getElementsByTagName('g')
        for g in groups:
            paths = g.getElementsByTagName('path') + g.getElementsByTagName('circle')
            group_id = g.attributes['id'].value
            if group_id != 'bg':
                place_type = Place.PLACE_TYPE_SLUGS[group_id.upper()]
                print ('## ' + group_id + ':')
                to_be_added = []
                for path in paths:
                    code = unicode(path.attributes['data-code'].value).encode("utf-8")
                    name = unicode(path.attributes['data-name'].value).encode("utf-8")
                    if code.strip() == '' or code in too_small_places_codes:
                        continue
                    place = self.find_place_or_create_new(code, name, place_type)
                    to_be_added.append(place)
                relation.related_places.add(*to_be_added)

    def find_place_relation_or_create_new(self, place):
        try:
            place_relation = PlaceRelation.objects.get(place=place, type=PlaceRelation.IS_ON_MAP)
            place_relation.related_places.clear()
        except PlaceRelation.DoesNotExist:
            place_relation = PlaceRelation(place=place, type=PlaceRelation.IS_ON_MAP)
            place_relation.save()
        return place_relation

    def find_place_or_create_new(self, code, name, place_type=Place.UNKNOWN):
        if code in self.places_cache:
            return self.places_cache[code]
        try:
            place = Place.objects.get(code=code)
        except Place.DoesNotExist:
            place = Place(code=code, name=name, type=place_type)
            place.save()
            self.places_cache[code] = place
            print (code + "\t" + name)
        return place

    def get_all_places(self):
        return self.places_cache
