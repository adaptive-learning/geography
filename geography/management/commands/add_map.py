from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import json
import os
from xml.dom import minidom
from django.conf import settings
import codecs
import csv


class Command(BaseCommand):
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
                " <flashcards-file> <map-code>")
        with open(args[0], 'r') as json_file:
            map_code = args[1]
            data = json.load(json_file, 'utf-8')

        contexts_by_id = {}
        for c in data['contexts']:
            contexts_by_id[c['id']] = c
        if map_code not in contexts_by_id:
            print "missing map: %s" % map_code

        terms_by_id = {}
        for t in data['terms']:
            terms_by_id[t['id']] = t

        categories_by_id = {}
        for t in data['terms']:
            categories_by_id[t['id']] = t

        self.add_map(map_code, data, terms_by_id)
        self.update_translations(data, terms_by_id, categories_by_id)
        # self.generate_translations_file(data)

        with open(options['output'], 'w') as f:
            json.dump(data, f, indent=2)
            print ('Updated flashcards written to file: \'%s\'' %
                   options['output'])

    def generate_translations_file(self, data):
        for lang in settings.LANGUAGES:
            with codecs.open('data/translations_%s.csv' % lang[0], 'w', encoding='utf-8') as f:
                for category in data['categories']:
                    print category['name-' + lang[0]]
                    f.write(u'"%s","%s"\n' %
                            (category['id'], category.get('name-' + lang[0], '')))
                for term in data['terms']:
                    f.write(u'"%s","%s"\n' %
                            (term['id'], term.get('name-' + lang[0], '')))

    def update_translations(self, data, terms_by_id, categories_by_id):
        for lang in settings.LANGUAGES:
            with open('data/translations_%s.csv' % lang[0], 'r') as csvfile:
                translations_reader = csv.reader(csvfile, delimiter=',')
                for row in translations_reader:
                    code, name = row
                    if name != '':
                        if code in terms_by_id:
                            terms_by_id[code]['name-' + lang[0]] = name
                        if code in categories_by_id:
                            categories_by_id[code]['name-' + lang[0]] = name

    def add_map(self, map_code, data, terms_by_id):
        flashcards_by_id = {}
        for f in data['flashcards']:
            flashcards_by_id[f['id']] = f

        file_name = os.path.join(settings.BASE_DIR, 'geography/static/map/{0}.svg'.format(map_code))
        map_dom = minidom.parse(file_name)
        groups = map_dom.getElementsByTagName('g')
        for g in groups:
            paths = g.getElementsByTagName('path') + g.getElementsByTagName('circle')
            group_id = g.attributes['id'].value
            if group_id != 'bg':
                # place_type = Place.PLACE_TYPE_SLUGS[group_id.upper()]
                print ('## ' + group_id + ':')
                for path in paths:
                    code = unicode(path.attributes['data-code'].value).encode("utf-8")
                    name = unicode(path.attributes['data-name'].value).encode("utf-8")
                    if code not in terms_by_id:
                        term = {
                            'id': code,
                            'name-cs': name,
                            'type': group_id,
                            'categories': [map_code],
                        }
                        data['terms'].append(term)
                        flashcard = {
                            'id': map_code + '-' + code,
                            'term': code,
                            'context': map_code,
                            'description': code,
                        }
                        data['flashcards'].append(flashcard)
                        print 'Flashcard added: ' + name
                    elif map_code not in terms_by_id[code]['categories']:
                        terms_by_id[code]['categories'].append(map_code)
