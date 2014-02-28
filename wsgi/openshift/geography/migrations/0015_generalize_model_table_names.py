# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0014_add_fujian_to_cina")]

    def forwards(self, orm):
        cursor = connection.cursor()
        cursor.execute('RENAME TABLE geography_elodifficulty TO geography_difficulty')
        cursor.execute('RENAME TABLE geography_elolocalskill TO geography_currentskill')
        cursor.execute('RENAME TABLE geography_eloskill TO geography_priorskill')

    def backwards(self, orm):
        cursor = connection.cursor()
        cursor.execute('RENAME TABLE geography_difficulty TO geography_elodifficulty')
        cursor.execute('RENAME TABLE geography_currentskill TO geography_elolocalskill')
        cursor.execute('RENAME TABLE geography_priorskill TO geography_eloskill')

    complete_apps = ['geography']
