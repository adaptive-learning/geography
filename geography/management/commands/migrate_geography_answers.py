from django.core.management.base import BaseCommand
from optparse import make_option
from contextlib import closing
from django.db import connections, connection
from proso_flashcards.models import Flashcard
from proso_user.models import Location, Session
from collections import defaultdict
from django.db import transaction
from clint.textui import progress


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '--geography-database',
            dest='geography_database',
            type=str,
            default='default',
            help='Database where the data for geogaphy app is.'),
        make_option(
            '--clean',
            action='store_true',
            dest='clean',
            default=False,
            help='Delete all previously loaded data'),
        make_option(
            '--limit',
            dest='limit',
            default=1000000,
            type=int,
            help='Maximum number of loaded answer'),
        make_option(
            '--batch-size',
            dest='batch_size',
            default=100,
            type=int),
    )

    LANGUAGES = {
        0: 'cs',
        1: 'en',
        2: 'es'
    }

    DIRECTIONS = {
        1: 't2d',
        2: 'd2t'
    }

    def handle(self, *args, **options):
        with transaction.atomic():
            with closing(connection.cursor()) as cursor:
                cursor.execute('SET CONSTRAINTS ALL DEFERRED;')
            self.migrate_answers(options['geography_database'], clean=options['clean'], limit=options['limit'], batch_size=options['batch_size'])
        print ' -- commit transaction'

    def load_flashcards(self):
        return dict(map(lambda o: ((o.identifier, o.context.identifier, o.lang), o), list(Flashcard.objects.select_related('context').all())))

    def get_flashcard(self, map_code, place_code, lang, flashcards, mask=lambda o: o.item_id if o else None):
        if place_code is None:
            return None
        place_code_split = place_code.split('-')
        if len(place_code_split) > 1 and place_code_split[0] in ['cn', 'br', 'ar', 'mx', 'ca', 'gb', 'de', 'fr', 'es', 'at', 'in', 'au', 'sk', 'us', 'it', 'cz']:
            map_code = place_code_split[0]
        if map_code is not None:
            place_code = '%s-%s' % (map_code, place_code)
        flashcard = flashcards.get((place_code, map_code, lang))
        if flashcard is None:
            filtered = filter(lambda (k, v): (k[0].endswith(place_code) and k[2] == lang), flashcards.items())
            if len(filtered) == 0:
                raise FlashcardException("There is no flashcard: %s, %s, %s" % (place_code, map_code, lang))
            if len(filtered) == 1:
                flashcards[place_code, map_code, lang] = filtered[0][1]
                return mask(filtered[0][1])
            filtered_dict = dict(filtered)
            map_codes = ['world', 'europe', 'africa', 'asia', 'namerica', 'samerica', 'oceania']
            for mc in map_codes:
                flashcard = filtered_dict.get((place_code, mc, lang))
                if flashcard:
                    flashcards[place_code, map_code, lang] = flashcard
                    return mask(flashcard)
            flashcards[place_code, map_code, lang] = filtered[0][1]
            return mask(filtered[0][1])
        return mask(flashcard)

    def migrate_answers(self, source_database, clean=True, limit=1000000, batch_size=100):
        prev_max_answer = 0
        if clean:
            print ' -- delete answers'
            with closing(connection.cursor()) as cursor:
                cursor.execute('TRUNCATE TABLE proso_flashcards_flashcardanswer_options CASCADE')
                cursor.execute('TRUNCATE TABLE proso_flashcards_flashcardanswer CASCADE')
                cursor.execute('TRUNCATE TABLE proso_models_answer_ab_values CASCADE')
                cursor.execute('TRUNCATE TABLE proso_models_answer CASCADE')
                cursor.execute('TRUNCATE TABLE proso_user_session CASCADE')
                cursor.execute('TRUNCATE TABLE proso_user_location CASCADE')
        else:
            with closing(connection.cursor()) as cursor:
                cursor.execute('SELECT MAX(id) FROM proso_models_answer')
                prev_max_answer, = cursor.fetchone()
                if prev_max_answer is None:
                    prev_max_answer = 0
        print ' -- load flashcards'
        flashcards = self.load_flashcards()
        print ' -- prepare retrievers'
        geography_options = GeographyOptions(source_database, limit)
        geography_sessions = Sessions()
        geography_ab_values = GeographyABValues(source_database, limit)
        print ' -- start migrating', limit, 'answers, from', prev_max_answer
        with closing(connections[source_database].cursor()) as cursor_source:
            cursor_source.execute(
                '''
                SELECT
                    user_id,
                    place_asked.code,
                    place_answered.code,
                    geography_answer.type,
                    inserted,
                    response_time,
                    place_map.code,
                    ip_address,
                    language,
                    geography_answer.id,
                    number_of_options
                FROM geography_answer
                INNER JOIN geography_place AS place_asked ON place_asked.id = geography_answer.place_asked_id
                LEFT JOIN geography_place AS place_answered ON place_answered.id = geography_answer.place_answered_id
                LEFT JOIN geography_place AS place_map ON place_map.id = geography_answer.place_map_id
                WHERE geography_answer.id > %s
                ORDER BY geography_answer.id
                LIMIT %s
                ''', [prev_max_answer, limit])
            with closing(connection.cursor()) as cursor_dest:
                progress_bar = progress.bar(cursor_source, every=max(1, cursor_source.rowcount / 100), expected_size=cursor_source.rowcount)
                all_option_values = []
                all_ab_values = []
                for row in progress_bar:
                    if len(all_option_values) >= batch_size:
                        self.insert_batch(
                            cursor_dest,
                            'proso_flashcards_flashcardanswer_options',
                            ['flashcardanswer_id', 'flashcard_id'],
                            all_option_values)
                        all_option_values = []
                    if len(all_ab_values) >= batch_size:
                        self.insert_batch(
                            cursor_dest,
                            'proso_models_answer_ab_values',
                            ['answer_id', 'value_id'],
                            all_ab_values)
                        all_ab_values = []
                    try:
                        general_answer_id = row[9]
                        lang = self.LANGUAGES[row[8]]
                        item_asked_id = self.get_flashcard(row[6], row[1], lang, flashcards)
                        item_id = item_asked_id
                        item_answered_id = self.get_flashcard(row[6], row[2], lang, flashcards)
                        guess = 0 if row[10] == 0 else 1.0 / row[10]
                        direction = self.DIRECTIONS[row[3]]
                        cursor_dest.execute(
                            '''
                            INSERT INTO proso_models_answer
                                (id, user_id, item_id, item_asked_id, item_answered_id, time, response_time, ab_values_initialized, session_id, guess)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ''', [general_answer_id, row[0], item_id, item_asked_id, item_answered_id, row[4], row[5], True, geography_sessions.get_session_id(row[0], row[7], lang, row[4]), guess])
                        cursor_dest.execute(
                            '''
                            INSERT INTO proso_flashcards_flashcardanswer
                                (direction, answer_ptr_id)
                            VALUES (%s, %s)
                            ''', [direction, general_answer_id])
                        options = geography_options.get_options(general_answer_id)
                        if len(options) > 0:
                            all_option_values.extend(map(
                                lambda i: (general_answer_id, self.get_flashcard(row[6], i, lang, flashcards, mask=lambda o: o.id if o else None)),
                                options))
                        ab_values = geography_ab_values.get_values(general_answer_id)
                        if len(ab_values) > 0:
                            all_ab_values.extend(map(lambda v: (general_answer_id, v), ab_values))
                    except FlashcardException as e:
                        print general_answer_id, '|', str(e)
                if len(all_option_values) > 0:
                    self.insert_batch(
                        cursor_dest,
                        'proso_flashcards_flashcardanswer_options',
                        ['flashcardanswer_id', 'flashcard_id'],
                        all_option_values)
                if len(all_ab_values) > 0:
                    self.insert_batch(
                        cursor_dest,
                        'proso_models_answer_ab_values',
                        ['answer_id', 'value_id'],
                        all_ab_values)

    def insert_batch(self, cursor, table_name, columns, values_list):
        pattern = '(' + ','.join(['{}' for i in columns]) + ')'
        values = map(lambda vals: pattern.format(*vals), values_list)
        cursor.execute('INSERT INTO {} ({}) VALUES {}'.format(
            table_name,
            ','.join(columns),
            ','.join(values)
        ))

class FlashcardException(Exception):
    pass


class GeographyOptions:

    def __init__(self, source_database, batch_size=100000):
        self._cache = None
        self._max_answer_id = 0
        self._batch_size = batch_size
        self._source_database = source_database

    def get_options(self, answer_id):
        if answer_id > self._max_answer_id:
            self._load_batch(answer_id)
        return self._cache[answer_id]

    def _load_batch(self, answer_id):
        with closing(connections[self._source_database].cursor()) as cursor:
            cursor.execute(
                '''
                SELECT answer_id, place.code
                FROM geography_answer_options
                LEFT JOIN geography_place AS place ON place.id = place_id
                WHERE answer_id >= %s AND answer_id <= %s
                ''', [answer_id, answer_id + self._batch_size])
            result = defaultdict(list)
            self._max_answer_id = self._max_answer_id + self._batch_size
            for row in cursor:
                self._max_answer_id = max(self._max_answer_id, row[0])
                result[row[0]].append(row[1])
            self._cache = result


class Sessions:

    def __init__(self):
        self._sessions = {}

    def get_session_id(self, user, ip_address, locale, time):
        if ip_address is None or ip_address == '':
            return None
        found = self._sessions.get(user)
        if found is None:
            session, session_time = self._new_session(user, locale, ip_address), time
        else:
            session, session_time = found
            if session.location.ip_address != ip_address or (time - session_time).total_seconds() > 30 * 60:
                session = self._new_session(user, locale, ip_address)
        self._sessions[user] = session, time
        return session.id

    def _new_session(self, user, locale, ip_address):
        location = Location(ip_address=ip_address)
        location.save()
        session = Session(location=location, user_id=int(user), locale=locale)
        session.save()
        return session


class GeographyABValues:

    def __init__(self, source_database, batch_size=100000):
        self._cache = None
        self._max_answer_id = 0
        self._batch_size = batch_size
        self._source_database = source_database

    def get_values(self, answer_id):
        if answer_id > self._max_answer_id:
            self._load_batch(answer_id)
        return self._cache[answer_id]

    def _load_batch(self, answer_id):
        with closing(connections[self._source_database].cursor()) as cursor:
            cursor.execute(
                '''
                SELECT answer_id, value_id
                FROM geography_answer_ab_values
                WHERE answer_id >= %s AND answer_id <= %s
                ''', [answer_id, answer_id + self._batch_size])
            result = defaultdict(list)
            self._max_answer_id = self._max_answer_id + self._batch_size
            for row in cursor:
                self._max_answer_id = max(self._max_answer_id, row[0])
                result[row[0]].append(row[1])
            self._cache = result
