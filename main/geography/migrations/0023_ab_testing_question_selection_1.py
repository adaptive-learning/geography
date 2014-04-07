# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.core.management import call_command
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0022_ab_testing_unique")]


    def forwards(self, orm):
        call_command(
            'ab_testing',
            'init',
            'question_selection_1=recommendation_by_additive_function',
            'recommendation_by_additive_function=90',
            'recommendation_by_random=10',
            max_answers=1)

    def backwards(self, orm):
        pass

    complete_apps = ['geography']
