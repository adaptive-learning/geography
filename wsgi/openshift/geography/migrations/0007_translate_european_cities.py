
# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):
    TRANSLATE = {
        u'Luxembourg': u'Lucemburk',
        u'Monaco': u'Monako',
        u'Ljubljana': u'Lublaň',
        u'Pristina': u'Priština',
        u'Chisinau': u'Kišiněv',
        u'Zagreb': u'Záhřeb',
        u'Tallinn': u'Talinn',
        u'Belgrade': u'Bělehrad',
        u'Sofia': u'Sofie',
        u'Budapest': u'Budapešť',
        u'Bucharest': u'Bukurešť',
        u'Lisbon': u'Lisabon',
        u'Warsaw': u'Varšava',
        u'Prague': u'Praha',
        u'København': u'Kodaň',
        u'Brussels': u'Brusel',
        u'Kiev': u'Kyjev',
        u'Geneva': u'Ženeva',
        u'Berlin': u'Berlín',
        u'Athens': u'Athény',
        u'Vienna': u'Vídeň',
        u'London': u'Londýn',
        u'Moscow': u'Moskva',
        u'Rome': u'Řím',
        u'Paris': u'Paříž',
    }

    dependencies = [("migrations", "0006_add_european_cities")]

    def forwards(self, orm):
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
