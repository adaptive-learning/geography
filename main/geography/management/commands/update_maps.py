# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from geography.management import MapUpdater
from geography.models import Place
import csv
import settings


class Command(BaseCommand):
    help = u"""Add new places"""

    def handle(self, *args, **options):
        u = MapUpdater()
        u.update_all_maps()
        all_places = u.get_all_places()
        for lang in settings.LANGUAGES:
            self.translate(all_places, lang[0])

    def translate(self, all_places, lang_code):
        translations = self.get_translations(lang_code)
        print "Applying translations: " + lang_code
        for code, name in translations:
            if code in all_places:
                place = all_places[code]
                name = unicode(name, 'utf-8')
                if getattr(place, 'name_' + lang_code) != name:
                    setattr(place, 'name_' + lang_code, name)
                    place.save()
            else:
                print "Warning: bad place code: " + code
        places_with_empty_names = Place.objects.filter(**{'name_' + lang_code: None})
        for place in places_with_empty_names:
            if place.name_en is not None:
                setattr(place, 'name_' + lang_code, place.name_en)
                place.save()
        print "Done"

    def get_translations(self, lang_code):
        translations = []
        with open(settings.PROJECT_DIR + '/translations_' + lang_code + '.csv', 'rb') as csvfile:
            translations_reader = csv.reader(csvfile, delimiter='\t')
            for row in translations_reader:
                if len(row) == 2:
                    translations.append(row)
        return translations
