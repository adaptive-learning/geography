# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.core.management import call_command


class Migration(DataMigration):

    dependencies = [("migrations", "0005_fix_codes_of_de_and_at")]

    def forwards(self, orm):
        call_command('add_map', 'europe', u'Evropa', 'CITY')

    def backwards(self, orm):
        pass

    complete_apps = ['geography']
