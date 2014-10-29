# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from contextlib import closing
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0034_add_model_Goal")]

    def forwards(self, orm):
        with closing(connection.cursor()) as cursor:
            cursor.execute('UPDATE geography_test SET active = 0')

    def backwards(self, orm):
        with closing(connection.cursor()) as cursor:
            cursor.execute('UPDATE geography_test SET active = 1')

    complete_apps = ['geography']
