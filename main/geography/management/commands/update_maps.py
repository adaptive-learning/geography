from django.core.management.base import BaseCommand
from geography.management import MapUpdater
from django.db import connection
import csv
import settings


class Command(BaseCommand):
    help = u"""Add new places"""

    def handle(self, *args, **options):
        u = MapUpdater()
        u.update_all_maps()
        self.translate()

    def translate(self):
        translations = self.get_translations()
        cursor = connection.cursor()
        print "Applying translations"
        for code, name in translations:
            cursor.execute(
                '''
                UPDATE
                    geography_place
                SET
                    name = %s
                WHERE code = %s OR name = %s
                ''',
                [name, code, code]
            )
        print "Done"

    def get_translations(self):
        translations = []
        with open(settings.PROJECT_DIR + '/translations.csv', 'rb') as csvfile:
            translations_reader = csv.reader(csvfile, delimiter='\t')
            for row in translations_reader:
                if len(row) == 2:
                    translations.append(row)
        return translations
