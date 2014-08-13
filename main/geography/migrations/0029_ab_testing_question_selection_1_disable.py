# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.core.management import call_command

class Migration(DataMigration):

    dependencies = [("migrations", "0028_myisam2innodb_test")]


    def forwards(self, orm):
        call_command(
            'ab_testing',
            'disable',
            'question_selection_1')

    def backwards(self, orm):
        call_command(
            'ab_testing',
            'enable',
            'question_selection_1')

    complete_apps = ['geography']
