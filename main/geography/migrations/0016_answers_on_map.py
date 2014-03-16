# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0015_generalize_model_table_names")]

    def forwards(self, orm):
        cursor = connection.cursor()
        cursor.execute(
            '''
            ALTER TABLE geography_answer ADD COLUMN place_map_id INTEGER
            ''')
        cursor.execute(
            '''
            ALTER TABLE geography_answer
            ADD CONSTRAINT place_map_id_refs_id_aa6d0cc6
                FOREIGN KEY (place_map_id) REFERENCES geography_place (id)
            ''')

    def backwards(self, orm):
        cursor = connection.cursor()
        cursor.execute('ALTER TABLE geography_answer DROP FOREIGN KEY place_map_id_refs_id_aa6d0cc6')
        cursor.execute('ALTER TABLE geography_answer DROP COLUMN place_map_id')

    complete_apps = ['geography']
