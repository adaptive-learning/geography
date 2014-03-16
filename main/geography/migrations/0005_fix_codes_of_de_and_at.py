# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):
    NEW_CODES = {
        u'Nordrhein-Westfalen': u'de-nw',
        u'Baden-Württemberg': u'de-bw',
        u'Hessen': u'de-he',
        u'Bremen': u'de-hb',
        u'Niedersachsen': u'de-ni',
        u'Thüringen': u'de-th',
        u'Hamburg': u'de-hh',
        u'Schleswig-Holstein': u'de-sh',
        u'Rheinland-Pfalz': u'de-rp',
        u'Saarland': u'de-sl',
        u'Bayern': u'de-by',
        u'Berlin': u'de-be',
        u'Sachsen-Anhalt': u'de-st',
        u'Sachsen': u'de-sn',
        u'Brandenburg': u'de-br',
        u'Mecklenburg-Vorpommern': u'de-mv',
        u'Vorarlberg': u'at-vo',
        u'Burgenland': u'at-bu',
        u'Steiermark': u'at-st',
        u'Kärnten': u'at-ka',
        u'Oberösterreich': u'at-oo',
        u'Salzburg': u'at-sz',
        u'Tirol': u'at-tr',
        u'Niederösterreich': u'at-no',
        u'Wien': u'at-wi',
    }

    dependencies = [("migrations", "0004_add_too_small_states")]

    def forwards(self, orm):
        cursor = connection.cursor()
        for old, new in Migration.NEW_CODES.iteritems():
            cursor.execute(
                '''
                UPDATE
                    geography_place
                SET
                    code = %s
                WHERE code = %s
                ''',
                [new, old]
            )

    def backwards(self, orm):
        pass

    complete_apps = ['geography']
