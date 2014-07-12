# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0031_ab_testing_target_probability_1")]

    def forwards(self, orm):
        cursor = connection.cursor()
        cursor.execute('ALTER TABLE `geography_place` ADD COLUMN `name_cs` varchar(100)')
        cursor.execute('ALTER TABLE `geography_place` ADD COLUMN `name_en` varchar(100)')

    def backwards(self, orm):
        cursor = connection.cursor()
        cursor.execute('ALTER TABLE `geography_place` DROP COLUMN `name_cs`')
        cursor.execute('ALTER TABLE `geography_place` DROP COLUMN `name_en`')

    complete_apps = ['geography']
