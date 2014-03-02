# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.core.management import call_command
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0017_add_usa_cities_and_auropean_mountains")]

    TRANSLATE = {
        # Germany
        u'Bielefeld': u'Bielefeld',
        u'Dortmund': u'Dortmund',
        u'Duisburg': u'Duisburg',
        u'Wuppertal': u'Wuppertal',
        u'Essen': u'Essen',
        u'Karlsruhe': u'Karlsruhe',
        u'Heidelberg': u'Heidelberg',
        u'Augsburg': u'Augsburg',
        u'Chemnitz': u'Chemnitz',
        u'Bonn': u'Bonn',
        u'Ddsseldorf': u'Düsseldorf',
        u'Mannheim': u'Mannheim',
        u'Wiesbaden': u'Wiesbaden',
        u'Hannover': u'Hannover',
        u'Koblenz': u'Koblenz',
        u'Saarbrucken': u'Saarbrücken',
        u'Leipzig': u'Lipsko',
        u'Stuttgart': u'Stuttgart',
        u'Bremen': u'Brémy',
        u'Nornberg': u'Norimberk',
        u'Cologne': u'Kolín nad Rýnem',
        u'Dresden': u'Drážďany',
        u'Frankfurt': u'Frankfurt',
        u'Hamburg': u'Hamburg',
        u'Munich': u'Mnichov',
        u'Berlin': u'Berlín',
        # Austria
        u'Vienna': u'Vídeň',
        u'Passau': u'Pasov',
        # France
        u'Reims': u'Remeš',
        u'Strasbourg': u'Štrasburk',
        u'Paris': u'Paříž',
        # Italy
        u'Trieste': u'Terst',
        u'Genoa': u'Janov',
        u'Turin': u'Turín',
        u'Siracusa': u'Syracusy',
        u'Venice': u'Benátky',
        u'Naples': u'Neapol',
        u'Milan': u'Milán',
        u'Rome': u'Řím',
        u'Florence': u'Florencie',
        # Spain
        u'La Coruea': u'A Coruña',
        u'Seville': u'Sevilla',
    }

    def forwards(self, orm):
        call_command('add_map', 'de', u'Německo', 'CITY')
        call_command('add_map', 'ca', u'N', 'CITY')
        call_command('add_map', 'au', u'N', 'CITY')
        call_command('add_map', 'at', u'N', 'CITY')
        call_command('add_map', 'cz', u'N', 'CITY')
        call_command('add_map', 'fr', u'N', 'CITY')
        call_command('add_map', 'it', u'N', 'CITY')
        call_command('add_map', 'es', u'N', 'CITY')

        cursor = connection.cursor()
        for code, name in Migration.TRANSLATE.iteritems():
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

    def backwards(self, orm):
        pass

    complete_apps = ['geography']
