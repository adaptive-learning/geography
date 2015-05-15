from django.core.management.base import BaseCommand
from django.core.management import call_command
from optparse import make_option
from contextlib import closing
from django.db import connections
import json


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '--geography-database',
            dest='geography_database',
            type=str,
            default='default',
            help='Database where the data for geogaphy app is.'),
        make_option(
            '--dry',
            dest='dry',
            action='store_true',
            default=False),
    )

    PLACE_TYPES = {
        0: 'unknown',
        1: 'state',
        2: 'city',
        3: 'world',
        4: 'continent',
        5: 'river',
        6: 'lake',
        7: 'region_cz',
        8: 'bundesland',
        9: 'province',
        10: 'region_it',
        11: 'region',
        12: 'autonomous_Comunity',
        13: 'mountains',
        14: 'island'
    }

    def handle(self, *args, **options):
        categories = self.migrate_categories(options['geography_database'])
        terms, categories, flashcards_to_ignore = self.migrate_terms(categories, options['geography_database'])
        flashcards, contexts = self.migrate_contexts(categories, terms, flashcards_to_ignore, options['geography_database'])
        with open('geography-flashcards.json', 'w') as f:
            json.dump({
                'categories': categories.values(),
                'terms': terms.values(),
                'flashcards': flashcards,
                'contexts': contexts.values()
            }, f, indent=2)
        if not options['dry']:
            call_command('load_flashcards', 'geography-flashcards.json')

    def migrate_contexts(self, categories, terms, flashcards_to_ignore, source_database):

        def _category2context(c):
            return {
                'id': c['id'],
                'content-cs': '%s.svg' % c['id'],
                'content-en': '%s.svg' % c['id'],
                'content-es': '%s.svg' % c['id'],
                'name-cs': c['name-cs'],
                'name-en': c['name-en'],
                'name-es': c['name-es']
            }
        contexts = dict(map(lambda c: (c['id'], _category2context(c)), categories.values()))
        flashcards = []
        for term in terms.itervalues():
            for category in term['categories']:
                flashcard = {
                    'id': '%s-%s' % (category, term['id']),
                    'term': term['id'],
                    'description': term['id'],
                    'context': contexts[category]['id']
                }
                if (category, term['id']) in flashcards_to_ignore:
                    flashcard['active'] = False
                    print ' XXX deactivating flashcard', flashcard['id']
                flashcards.append(flashcard)
        return flashcards, contexts

    def migrate_terms(self, categories, source_database):
        terms = {}
        used_categories = {}
        flashcards_to_ignore = set()
        with closing(connections[source_database].cursor()) as cursor:
            cursor.execute(
                '''
                SELECT
                    id,
                    code,
                    name,
                    type,
                    name_cs,
                    name_en,
                    name_es
                FROM geography_place
                ''')
            for row in cursor:
                term = {
                    'id': row[1],
                    'type': self.PLACE_TYPES[row[3]],
                    'name-cs': row[4],
                    'name-en': row[5],
                    'name-es': row[6],
                    'categories': []
                }
                if not term['name-en']:
                    print ' XXX there is no english translation for map', row[1]
                    term['name-en'] = row[2]
                if not term['name-cs']:
                    print ' XXX there is no czech translation for map', row[1]
                    term['name-cs'] = term['name-en']
                if not term['name-es']:
                    print ' XXX there is no spanish translation for map', row[1]
                    term['name-es'] = term['name-en']
                terms[row[0]] = term
        with closing(connections[source_database].cursor()) as cursor:
            cursor.execute(
                '''
                SELECT
                    geography_placerelation.place_id AS map_id,
                    geography_placerelation_related_places.place_id AS place_id,
                    type
                FROM geography_placerelation
                INNER JOIN geography_placerelation_related_places ON
                    geography_placerelation.id = geography_placerelation_related_places.placerelation_id
                WHERE type = 1 OR type = 4
                ''')
            for row in cursor:
                terms[row[1]]['categories'].append(categories[row[0]]['id'])
                used_categories[row[0]] = categories[row[0]]
                if row[2] == 4:
                    flashcards_to_ignore.add((categories[row[0]]['id'], terms[row[1]]['id']))
        return terms, used_categories, flashcards_to_ignore

    def migrate_categories(self, source_database):
        categories = {}
        with closing(connections[source_database].cursor()) as cursor:
            cursor.execute(
                '''
                SELECT
                    geography_place.id,
                    geography_place.code,
                    geography_place.name,
                    geography_place.type,
                    geography_place.name_cs,
                    geography_place.name_en,
                    geography_place.name_es
                FROM geography_place
                INNER JOIN geography_placerelation ON
                    geography_place.id = geography_placerelation.place_id
                ''')
            for row in cursor:
                category = {
                    'id': row[1],
                    'type': self.PLACE_TYPES[row[3]],
                    'name-cs': row[4],
                    'name-en': row[5],
                    'name-es': row[6]
                }
                if not category['name-en']:
                    print ' XXX there is no english translation for map', row[1]
                    category['name-en'] = row[2]
                if not category['name-cs']:
                    print ' XXX there is no czech translation for map', row[1]
                    category['name-cs'] = category['name-en']
                if not category['name-es']:
                    print ' XXX there is no spanish translation for map', row[1]
                    category['name-es'] = category['name-en']
                categories[row[0]] = category
        return categories
