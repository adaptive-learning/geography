# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import connection


class Migration(DataMigration):

    dependencies = [("migrations", "0027_test_europe_countries")]

    tables = [
        'geography_test',
        'geography_test_places_to_ask'
    ]

    def forwards(self, orm):
        cursor = connection.cursor()
        for table in self.tables:
            print 'InnoDB:', table
            cursor.execute('ALTER TABLE ' + table + ' ENGINE=InnoDB;')

    def backwards(self, orm):
        print 'nothing to do'

    complete_apps = ['geography']
