# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.core.management import call_command
from geography.models import Place

class Migration(DataMigration):

    dependencies = [("migrations", "0026_schema_test")]


    def forwards(self, orm):
        call_command(
            'testing',
            'init',
            map_code='europe',
            place_type=Place.STATE)

    def backwards(self, orm):
        pass

    complete_apps = ['geography']
