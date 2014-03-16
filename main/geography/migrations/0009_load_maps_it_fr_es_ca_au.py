# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.core.management import call_command


class Migration(DataMigration):

    dependencies = [("migrations", "0008_fix_codes_of_in")]

    def forwards(self, orm):
        call_command('add_map', 'it', u'', 'REGION_IT')
        call_command('add_map', 'fr', u'', 'REGION')
        call_command('add_map', 'es', u'', 'AUTONOMOUS_COMUNITY')
        call_command('add_map', 'ca', u'', 'PROVINCE')
        call_command('add_map', 'au', u'', 'STATE')

    def backwards(self, orm):
        pass

    complete_apps = ['geography']
