# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.core.management import call_command
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0001_migrating_data")]

    def forwards(self, orm):
        call_command('add_map', 'cz', u'Česká republika', 'REGION')
        call_command('add_map', 'de', u'Česká republika', 'BUNDESLAND')
        call_command('add_map', 'at', u'Česká republika', 'BUNDESLAND')
        call_command('add_map', 'in', u'Česká republika', 'STATE')
        call_command('add_map', 'cn', u'Česká republika', 'PROVINCE')
        cursor = connection.cursor()

    def backwards(self, orm):
        pass

    complete_apps = ['geography']
