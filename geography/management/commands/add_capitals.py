from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import json
import unicodecsv


class Command(BaseCommand):
    MAPS_DIR = 'geography/static/map'
    option_list = BaseCommand.option_list + (
        make_option(
            '--output',
            dest='output',
            type=str,
            default='new-flashcards.json'),
    )

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError(
                "Not enough arguments. Two arguments required: " +
                " <flashcards-file> <capitals-file>")
        with open(args[0], 'r') as json_file:
            data = json.load(json_file, 'utf-8')
        with open(args[1], 'r') as csvfile:
            capitals_reader = unicodecsv.reader(
                csvfile, delimiter=',', encoding='utf-8')
            capitals_dict = {}
            states_dict = {}
            for row in capitals_reader:
                if len(row) == 2:
                    capitals_dict[row[0]] = row[1]
                    states_dict[row[1]] = row[0]

        self.add_capitals(data, capitals_dict, 'europe', 'state', 'city')
        self.add_capitals(data, states_dict, 'europe', 'city', 'state')

        with open(options['output'], 'w') as f:
            json.dump(data, f, indent=2)
            print ('Updated flashcards written to file: \'%s\'' %
                   options['output'])

    def add_capitals(self, data, capitals_dict, map_code, from_type, to_type):
        cities_by_id = {}
        codes = {}
        for t in data['terms']:
            if t['type'] == to_type and map_code in t['categories']:
                cities_by_id[t['id']] = t
                codes[t['name-en']] = t['id']
        for t in data['terms']:
            if t['type'] == from_type and map_code in t['categories']:
                if t['name-en'] not in capitals_dict or capitals_dict[t['name-en']] not in codes:
                    print 'Warning: missing: ' + t['name-en']
                    continue
                capital_id = codes[capitals_dict[t['name-en']]]
                capital = cities_by_id[capital_id]
                new_term = {
                    'id': t['id'] + '-by-' + to_type,
                    'name-cs': capital['name-cs'],
                    'name-en': capital['name-en'],
                    'categories': [map_code],
                    'type': from_type + '-by-' + to_type,
                }
                data['terms'].append(new_term)
                data['flashcards'].append({
                    'id': map_code + '-' + new_term['id'],
                    'term': new_term['id'],
                    'context': map_code,
                    'description': t['id'],
                })
