# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.core.management import call_command

class Migration(DataMigration):

    dependencies = [("migrations", "0036_ab_testing_target_probability_extend")]


    def forwards(self, orm):
        call_command(
            'ab_testing',
            'init',
            'target_probability_adjustment=recommendation_target_prob_adjustment_true',
            'recommendation_target_prob_adjustment_true=50',
            'recommendation_target_prob_adjustment_false=50',
            max_answers=1)

    def backwards(self, orm):
        pass

    complete_apps = ['geography']
