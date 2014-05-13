# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from geography.models import KnowledgeUpdater, InMemoryEnvironmentWithFlush
from geography.models.utils import fetchone
from contextlib import closing


class Command(BaseCommand):
    help = u'''Recompute derived data'''

    def handle(self, *args, **options):
        if len(args) > 0:
            raise CommandError('The command doesn\'t need any option.')
        self.load_derived_data()

    def load_derived_data(self):
        connection.enter_transaction_management(False)
        with closing(connection.cursor()) as cursor_answers:
            with closing(connection.cursor()) as cursor_options:
                # foreach answer update new datasets
                print 'loading options'
                cursor_options.execute(
                    '''
                    SELECT
                        answer_id,
                        place_id
                    FROM geography_answer_options
                    ORDER BY answer_id
                    ''')
                row = cursor_options.fetchone()
                current_options = []
                last_options = None
                current_answer = -1
                last_answer = None
                print 'loading answers'
                cursor_answers.execute(
                    '''
                    SELECT
                        id,
                        user_id AS user,
                        place_asked_id AS place_asked,
                        place_answered_id AS place_answered,
                        place_map_id AS place_map,
                        inserted,
                        response_time,
                        number_of_options,
                        type
                    FROM geography_answer
                    ORDER BY id
                    ''')

                print 'computing knowledge data in memory'
                answer = fetchone(cursor_answers)
                env = InMemoryEnvironmentWithFlush()
                stream = KnowledgeUpdater(env)
                while answer:
                    while current_answer <= answer['id'] and row:
                        current_options.append(row[1])
                        row = cursor_options.fetchone()
                        if not row or row[0] != current_answer:
                            last_answer = current_answer
                            last_options = current_options
                            current_answer = row[0] if row else None
                            current_options = []
                    if last_answer == answer['id']:
                        answer['options'] = last_options
                    else:
                        answer['options'] = []
                    stream.stream_answer(answer)
                    answer = fetchone(cursor_answers)
        # empty precomputed datasets
        with closing(connection.cursor()) as cursor:
            cursor.execute('DELETE FROM geography_difficulty')
        with closing(connection.cursor()) as cursor:
            cursor.execute('DELETE FROM geography_priorskill')
        with closing(connection.cursor()) as cursor:
            cursor.execute('DELETE FROM geography_currentskill')
        # save new precomputed datasets
        print 'flushing knowledge data to database'
        env.flush()
        connection.commit()
