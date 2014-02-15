# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0011_translate_it_fr_es_ca_au")]

    def forwards(self, orm):
        cursor = connection.cursor()
        cursor.execute(
            '''
            CREATE INDEX geography_answer_last_index
            ON geography_answer (
                user_id,
                place_asked_id,
                inserted
            );
            ''')
        cursor.execute(
            '''
            CREATE INDEX geography_answer_places_index
            ON geography_answer (
                place_asked_id,
                place_answered_id
            );
            ''')

    def backwards(self, orm):
        cursor = connection.cursor()
        cursor.execute(
            '''
            DROP INDEX geography_answer_last_index
            ON geography_answer
            ''')
        cursor.execute(
            '''
            DROP INDEX geography_answer_places_index
            ON geography_answer
            ''')

    complete_apps = ['geography']
