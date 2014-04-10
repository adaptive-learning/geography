# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0023_ab_testing_question_selection_1")]

    tables = [
        'auth_user',
        'geography_place',
        'geography_ab_group',
        'geography_ab_value',
        'geography_ab_uservalues',
        'geography_ab_uservalues_values',
        'geography_answer',
        'geography_answer_ab_values',
        'geography_answer_options',
        'geography_currentskill',
        'geography_difficulty',
        'geography_elodifficulty',
        'geography_elolocalskill',
        'geography_eloskill',
        'geography_placerelation',
        'geography_placerelation_related_places',
        'geography_priorskill'
    ]

    def forwards(self, orm):
        cursor = connection.cursor()
        for table in self.tables:
            print 'InnoDB:', table
            cursor.execute('ALTER TABLE ' + table + ' ENGINE=InnoDB;')

    def backwards(self, orm):
        print 'nothing to do'

    complete_apps = ['geography']
