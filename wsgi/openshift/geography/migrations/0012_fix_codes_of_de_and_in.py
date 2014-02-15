# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):
    NEW_CODES = {
        u'de-br': u'de-bb',
        u'in-ta': u'in-tn',
        u'in-gu': u'in-gj',
    }

    dependencies = [("migrations", "0011_fix_codes_of_european_cities")]

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
