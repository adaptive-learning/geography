# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.core.management import call_command
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0016_answers_on_map")]

    TRANSLATE = {
        u'Hardanger-vidda': u'Hardangervidda',
        u'Böhmerwald': u'Šumava',
        u'Transylvanian Alps': u'Jižní Karpaty',
        u'Tatra_Mts.': u'Tatry',
        u'Pindus_Mts.': u'Pindos',
        u'Calabria': u'Kalábrie',
        u'Harz': u'Harz',
        u'Vosges': u'Vogézy',
        u'Sudetes_Mts.': u'Sudetská pohoří',
        u'Erzgebirge': u'Krušné hory',
        u'Ardennes': u'Ardeny',
        u'Jura': u'Jura',
        u'Grampian_Mts.': u'Grampiany',
        u'Cambrian_Mts.': u' Kumbrické hory',
        u'Balkan_Mts.': u'Stará planina',
        u'Dinaric_Alps': u'Dinárské hory',
        u'Cord._Cantábrica': u'Kantaberské pohoří',
        u'S._Nevada': u'Sierra Nevada',
        u'Sierra_Morena': u'Sierra Morena',
        u'KJLEN_MOUNTAINS': u'Skandinávské pohoří',
        u'CARPATHIAN_MOUNTAINS': u'Karpaty',
        u'APPENNINI': u'Apeniny',
        u'PYRENEES': u'Pyreneje',
        u'ALPS': u'Alpy',
        u'CAUCASUS_MTS.': u'Kavkaz',
    }

    def forwards(self, orm):
        call_command('add_map', 'europe', u'Evropa', 'MOUNTAINS')
        call_command('add_map', 'us', u'USA', 'CITY')

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
