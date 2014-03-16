
# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):
    NEW_CODES = {
        u'Chandigarh': u'in-ch',
        u'Delhi': u'in-dl',
        u'Himachal Pradesh': u'in-hp',
        u'Haryana': u'in-hr',
        u'Jammu and Kashmir': u'in-jk',
        u'Andhra Pradesh': u'in-ap',
        u'Kerala': u'in-kl',
        u'Lakshadweep': u'in-ld',
        u'Orissa': u'in-or',
        u'Dadra and Nagar Haveli': u'in-dn',
        u'Karnataka': u'in-ka',
        u'Maharashtra': u'in-mh',
        u'Andaman and Nicobar': u'in-an',
        u'Assam': u'in-as',
        u'Manipur': u'in-mn',
        u'Nagaland': u'in-nl',
        u'Meghalaya': u'in-ml',
        u'Punjab': u'in-pb',
        u'Rajasthan': u'in-rj',
        u'Uttar Pradesh': u'in-up',
        u'Uttaranchal': u'in-ut',
        u'Jharkhand': u'in-jh',
        u'West Bengal': u'in-wb',
        u'Bihar': u'in-br',
        u'Sikkim': u'in-sk',
        u'Chhattisgarh': u'in-ct',
        u'Madhya Pradesh': u'in-mp',
        u'Puducherry': u'in-py',
        u'Tamil Nadu': u'in-ta',
        u'Gujarat': u'in-gu',
        u'Goa': u'in-ga',
        u'Arunachal Pradesh': u'in-ar',
        u'Mizoram': u'in-mz',
        u'Tripura': u'in-tr',
    }

    dependencies = [("migrations", "0007_translate_european_cities")]

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
