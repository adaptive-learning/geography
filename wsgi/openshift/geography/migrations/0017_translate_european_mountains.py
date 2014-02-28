# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):
    TRANSLATE = {
        u'Hardanger-vidda': u'Hardangervidda',
        u'Böhmerwald': u'Šumava',
        u'Transylvanian Alps': u'Jižní Karpaty',
        u'Tatra Mts.': u'Tatry',
        u'Pindus Mts.': u'Pindos',
        u'Calabria': u'Kalábrie',
        u'Harz': u'Harz',
        u'Vosges': u'Vogézy',
        u'Sudetes Mts.': u'Sudetská pohoří',
        u'Erzgebirge': u'Krušné hory',
        u'Ardennes': u'Ardeny',
        u'Jura': u'Jura',
        u'Grampian Mts.': u'Grampiany',
        u'Cambrian Mts.': u' Kumbrické hory',
        u'Balkan Mts.': u'Stará planina',
        u'Dinaric Alps': u'Dinárské hory',
        u'Cord. Cantábrica': u'Kantaberské pohoří',
        u'S. Nevada': u'Sierra Nevada',
        u'Sierra Morena': u'Sierra Morena',
        u'KJØLEN MOUNTAINS': u'Skandinávské pohoří',
        u'CARPATHIAN MOUNTAINS': u'Karpaty',
        u'APPENNINI': u'Apeniny',
        u'PYRENEES': u'Pyreneje',
        u'ALPS': u'Alpy',
        u'CAUCASUS MTS.': u'Kavkaz',
    }

    dependencies = [("migrations", "0016_answers_on_map")]

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
