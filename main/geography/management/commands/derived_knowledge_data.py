# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from geography.models import KnowledgeUpdater, InMemoryEnvironmentWithFlush
from geography.models.utils import fetchone
from contextlib import closing
import time


class Command(BaseCommand):
    help = u'''Recompute derived data'''

    def handle(self, *args, **options):
        if len(args) > 0:
            raise CommandError('The command doesn\'t need any option.')
        self.load_derived_data()

    def load_derived_data(self):
        with closing(connection.cursor()) as cursor_answers:
            with closing(connection.cursor()) as cursor_options:
                # foreach answer update new datasets
                time_start = time.time()
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

                time_after_loading = time.time()
                print 'time:', (time_after_loading - time_start), 'secs'
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
                time_after_knowledge = time.time()
                print 'time:', (time_after_knowledge - time_after_loading), 'secs'
        # empty precomputed datasets
        print 'deleting old knowledge data from database'
        connection.enter_transaction_management(False)
        with closing(connection.cursor()) as cursor:
            cursor.execute('DELETE FROM geography_difficulty')
        with closing(connection.cursor()) as cursor:
            cursor.execute('DELETE FROM geography_priorskill')
        with closing(connection.cursor()) as cursor:
            cursor.execute('DELETE FROM geography_currentskill')
        time_after_delete = time.time()
        print 'time:', (time_after_delete - time_after_knowledge), 'secs'
        # save new precomputed datasets
        print 'flushing knowledge data to database'
        env.flush()
        time_after_flush = time.time()
        print 'time:', (time_after_flush - time_after_delete), 'secs'
        print 'database commit'
        connection.commit()
        print 'time:', (time.time() - time_after_flush), 'secs'
        print 'total time:', (time.time() - time_start), 'secs'
