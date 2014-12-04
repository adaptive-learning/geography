# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from geography.utils.db import dump_cursor
from contextlib import closing


class Command(BaseCommand):
    help = 'dump model to csv file'

    DEFAULT_BATCH_SIZE = 500000

    def handle(self, *args, **options):
        if len(args) != 2 and len(args) != 3:
            raise CommandError(
                '''
                The command requires exactly two arguments:
                    - table name
                    - destination file
                and one optional:
                    - batch size
                ''')
        table_name = args[0]
        dest_file = args[1]
        batch_size = self.DEFAULT_BATCH_SIZE if len(args) == 2 else int(args[2])
        allowed_tables = [
            'geography_ab_group',
            'geography_ab_value',
            'geography_answer',
            'geography_answer_ab_values',
            'geography_place',
            'geography_placerelation',
            'geography_answer_options',
            'geography_placerelation_related_places',
            'proso_feedback_rating'
        ]
        field_mapping = {
            'answer_id': 'answer',
            'group_id': 'group',
            'place_id': 'place',
            'place_asked_id': 'place_asked',
            'place_answered_id': 'place_answered',
            'place_map_id': 'place_map',
            'placerelation_id': 'placerelation',
            'user_id': 'user',
            'value_id': 'value'}
        if table_name in allowed_tables:
            count = 0
            with closing(connection.cursor()) as cursor:
                cursor.execute('SELECT COUNT(*) FROM ' + table_name + ' ORDER BY id')
                count, = cursor.fetchone()

            sql = 'SELECT * FROM ' + table_name
            for offset in xrange(0, count, batch_size):
                with closing(connection.cursor()) as cursor:
                    cursor = connection.cursor()
                    cursor.execute(sql + ' LIMIT ' + str(batch_size) + ' OFFSET ' + str(offset))
                    dump_cursor(
                        cursor,
                        dest_file,
                        append=(offset > 0),
                        **field_mapping)
        else:
            raise CommandError('table "' + table_name + '" is not supported')
