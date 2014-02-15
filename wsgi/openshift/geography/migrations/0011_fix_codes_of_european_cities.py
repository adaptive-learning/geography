# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):
    NEW_CODES = {
        u'Reykjavík': u'Reykjavik',
        u'København': u'Kobenhavn',
        u'San Marino': u'San_Marino',
    }

    dependencies = [("migrations", "0010_translate_it_fr_es_ca_au")]

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
