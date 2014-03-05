# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
import csv


class Command(BaseCommand):
    help = 'dump model to csv file'

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError(
                '''
                The command requires exactly two arguments:
                    - table name
                    - destination file
                ''')
        table_name = args[0]
        dest_file = args[1]
        allowed_tables = [
            'geography_answer',
            'geography_place',
            'geography_placerelation',
            'geography_answer_options',
            'geography_placerelation_related.places'
        ]
        field_mapping = {
            'answer_id': 'answer',
            'place_id': 'place',
            'place_asked_id': 'place_asked',
            'place_answered_id': 'place_answered',
            'place_map_id': 'place_map',
            'user_id': 'user'}
        if table_name in allowed_tables:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM ' + table_name)
            self.dump_cursor(
                cursor,
                dest_file,
                **field_mapping)
        else:
            raise CommandError('table ' + table_name + ' is not supported')

    def dump_cursor(self, cursor, dest_file, **field_mapping):
        headers = [field_mapping.get(col[0], col[0]) for col in cursor.description]
        with open(dest_file, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            row = cursor.fetchone()
            while row:
                row = [val.encode('utf-8') if isinstance(val, unicode) else val for val in row]
                writer.writerow(row)
                row = cursor.fetchone()
