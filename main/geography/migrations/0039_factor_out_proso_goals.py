# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0038_add_spanish_place_names.py")]

    def forwards(self, orm):
        cursor = connection.cursor()
        cursor.execute('RENAME TABLE `geography_goal` TO `proso_goals_goal` ')

    def backwards(self, orm):
        cursor = connection.cursor()
        cursor.execute('RENAME TABLE `proso_goals_goal` TO `geography_goal` ')

    complete_apps = ['geography']
