# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.core.management import call_command

class Migration(DataMigration):

    dependencies = [("migrations", "0029_ab_testing_question_selection_1_disable")]


    def forwards(self, orm):
        call_command(
            'ab_testing',
            'disable',
            'options_selection_1')

    def backwards(self, orm):
        call_command(
            'ab_testing',
            'enable',
            'options_selection_1')

    complete_apps = ['geography']
