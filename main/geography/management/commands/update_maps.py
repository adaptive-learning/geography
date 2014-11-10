# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from geography.management import MapUpdater
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
                if lang_code == 'en':
                    if place.name_en != name:
                        place.name_en = name
                        place.save()
                elif lang_code == 'cs':
                    if place.name_cs != name:
                        place.name_cs = name
                        place.save()
                elif lang_code == 'es':
                    if place.name_es != name:
                        place.name_es = name
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
