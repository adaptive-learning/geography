# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0037_ab_testing_target_probability_adjustment_1.py")]

    def forwards(self, orm):
        cursor = connection.cursor()
        cursor.execute('ALTER TABLE `geography_place` ADD COLUMN `name_es` varchar(100)')

    def backwards(self, orm):
        cursor = connection.cursor()
        cursor.execute('ALTER TABLE `geography_place` DROP COLUMN `name_es`')

    complete_apps = ['geography']
