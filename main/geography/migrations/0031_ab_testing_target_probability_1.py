# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.core.management import call_command
from geography.models import Place

class Migration(DataMigration):

    dependencies = [("migrations", "ab_testing_options_selection_1_disable")]


    def forwards(self, orm):
        call_command(
            'ab_testing',
            'init',
            'target_probability=recommendation_target_prob_80',
            'recommendation_target_prob_65=10',
            'recommendation_target_prob_70=10',
            'recommendation_target_prob_75=20',
            'recommendation_target_prob_80=20',
            'recommendation_target_prob_85=20',
            'recommendation_target_prob_90=10',
            'recommendation_target_prob_95=10',
            max_answers=1)

    def backwards(self, orm):
        pass

    complete_apps = ['geography']
