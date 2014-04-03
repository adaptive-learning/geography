# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0020_ab_testing_init_db_answers")]

    def forwards(self, orm):
        cursor = connection.cursor()
        cursor.execute(
            '''
            ALTER TABLE geography_answer ADD COLUMN ip_address VARCHAR(39);
            ''')

    def backwards(self, orm):
        cursor = connection.cursor()
        cursor.execute(
            '''
            ALTER TABLE geography_answer DROP COLUMN ip_address;
            ''')

    complete_apps = ['geography']
