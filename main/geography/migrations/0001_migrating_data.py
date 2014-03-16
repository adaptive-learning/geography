# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):

    def forwards(self, orm):
        cursor = connection.cursor()
        # move places
        cursor.execute('DELETE FROM geography_place')
        cursor.execute('DELETE FROM geography_placerelation')
        cursor.execute('DELETE FROM geography_placerelation_related_places')
        cursor.execute(
            '''
            INSERT INTO geography_place (id, code, name, type)
            SELECT id, code, name, type FROM core_place
            ''')
        cursor.execute(
            '''
            INSERT INTO geography_placerelation (id, place_id, type)
            SELECT id, place_id, type FROM core_placerelation
            '''
        )
        cursor.execute(
            '''
            INSERT INTO geography_placerelation_related_places (id, place_id, placerelation_id)
            SELECT id, place_id, placerelation_id FROM core_placerelation_related_places
            '''
        )
        # move answers
        cursor.execute('DELETE FROM geography_answer')
        cursor.execute('DELETE FROM geography_answer_options')
        cursor.execute(
            '''
            INSERT INTO geography_answer (
                id, user_id, place_asked_id, place_answered_id, type,
                inserted, response_time, number_of_options
            )
            SELECT
                core_answer.id AS id,
                core_student.user_id AS user_id,
                core_answer.place_id AS place_asked_id,
                core_answer.answer_id AS place_answered_id,
                LEFT(core_answer.type, 1) AS type,
                core_answer.askedDate AS inserted,
                core_answer.msResposeTime AS response_time,
                RIGHT(core_answer.type, 1) AS number_of_options
            FROM
                core_answer
                INNER JOIN core_student
                    ON core_answer.user_id = core_student.user_id
            ''')
        cursor.execute(
            '''
            INSERT INTO geography_answer_options (id, answer_id, place_id)
            SELECT id, answer_id, place_id FROM core_answer_options
            ''')

    def backwards(self, orm):
        cursor = connection.cursor()
        cursor.execute('DELETE FROM geography_place')
        cursor.execute('DELETE FROM geography_placerelation')
        cursor.execute('DELETE FROM geography_placerelation_related_places')
        cursor.execute('DELETE FROM geography_answer')
        cursor.execute('DELETE FROM geography_answer_options')

    complete_apps = ['geography']
