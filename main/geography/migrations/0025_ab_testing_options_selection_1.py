# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.core.management import call_command


class Migration(DataMigration):

    dependencies = [("migrations", "0024_myisam2innodb")]


    def forwards(self, orm):
        call_command(
            'ab_testing',
            'init',
            'options_selection_1=recommendation_options_naive',
            'recommendation_options_naive=70',
            'recommendation_options_random=30',
            max_answers=1)

    def backwards(self, orm):
        pass

    complete_apps = ['geography']
