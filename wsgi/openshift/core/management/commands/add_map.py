# -*- coding: utf-8 -*-

from core.models import Place, PlaceRelation
from django.core.management.base import BaseCommand, CommandError
import re



class Command(BaseCommand):
    help = u"""Add new places"""
                
    def handle(self, *args, **options):
        if(len(args) < 2):
            raise CommandError('Not enough arguments. Two arguments required: <slug> <displayName>')
        file_name = 'core/static/map/{0}.svg'.format(args[0])
        mapFile = open(file_name)
        map_data = mapFile.read()
        mapFile.close()
        
        mapFile = open(file_name, 'w')
        def dashrepl(matchobj):
            return  matchobj.group(0).lower() 
        map_data = re.sub(r'"[A-Z]{2}"', dashrepl, map_data)
        mapFile.write(map_data)
        mapFile.close()
        
        codes = re.findall(r'"[a-z]{2}"', map_data)
        codes = [c[1:3] for c in codes]
        places = Place.objects.all()
        new_place = Place(code=args[0], name=args[1], type=Place.CONTINENT)
        new_place.save()
        relation = PlaceRelation(place=new_place,type=PlaceRelation.IS_ON_MAP)
        relation.save()
        for p in places:
            if p.code in codes:
#                 self.stdout.write(p.name)
                relation.related_places.add(p)
        relation.save()
