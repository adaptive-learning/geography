from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import json
import os
from xml.dom import minidom
from django.conf import settings
import codecs
import csv


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
        if len(args) < 1:
            raise CommandError(
                "Not enough arguments. Two arguments required: " +
                " <flashcards-file> [<map-code>] [<lang-code>]")
        map_code = None
        if len(args) > 1:
            map_code = args[1]
        with open(args[0], 'r') as json_file:
            data = json.load(json_file, 'utf-8')
            data['contexts'] = data.get('contexts', [])
            data['terms'] = data.get('terms', [])
            data['categories'] = data.get('categories', [])
            data['flashcards'] = data.get('flashcards', [])
        if len(args) > 2:
            self.lang = args[2]
        else:
            self.lang = 'all'

        contexts_by_id = {}
        for c in data['contexts']:
            contexts_by_id[c['id']] = c
        terms_by_id = {}
        for t in data['terms']:
            terms_by_id[t['id']] = t

        categories_by_id = {}
        for t in data['terms']:
            categories_by_id[t['id']] = t

        if map_code is None:
            self.update_all_maps(data, terms_by_id)
        else:
            self.add_map(map_code, data, terms_by_id)
            if map_code not in contexts_by_id:
                self.add_context(data, map_code)

        self.update_translations(data, terms_by_id, categories_by_id)
        # self.generate_translations_file(data)

        with open(options['output'], 'w') as f:
            json.dump(data, f, indent=2)
            print(('Updated flashcards written to file: \'%s\'' %
                   options['output']))

    def add_context(self, data, map_code):
        names = {}
        for lang in settings.LANGUAGES:
            names[lang[0]] = self.get_translation(map_code, lang[0])
        context = {
            'id': map_code,
        }
        category = {
            'id': map_code,
            'type': 'state',  # TODO migh be not true in future
        }
        for lang in names.keys():
            context.update({
                'content-' + lang: map_code + '.svg',
                'name-' + lang: names[lang],
            })
            category.update({
                'name-' + lang: names[lang],
            })
        data['contexts'].append(context)
        data['categories'].append(category)
        print("missing map added: %s" % map_code)

    def get_translation(self, id, lang):
        with open('data/translations_%s.csv' % lang, 'r') as csvfile:
            translations_reader = csv.reader(csvfile, delimiter=',')
            for row in translations_reader:
                code, name = row
                if code == id:
                    return name

    def update_all_maps(self, data, terms_by_id):
        for f in sorted(os.listdir(os.path.join(settings.BASE_DIR, self.MAPS_DIR))):
            if f.endswith('.svg'):
                print('updating map: ' + f)
                self.add_map(f[:-4], data, terms_by_id)

    def generate_translations_file(self, data):
        for lang in settings.LANGUAGES:
            with codecs.open('data/translations_%s.csv' % lang[0], 'w', encoding='utf-8') as f:
                for category in data['categories']:
                    print(category['name-' + lang[0]])
                    f.write('"%s","%s"\n' %
                            (category['id'], category.get('name-' + lang[0], '')))
                for term in data['terms']:
                    f.write('"%s","%s"\n' %
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

        file_name = os.path.join(settings.BASE_DIR, self.MAPS_DIR, '{0}.svg'.format(map_code))
        map_dom = minidom.parse(file_name)
        groups = map_dom.getElementsByTagName('g')
        for g in groups:
            paths = g.getElementsByTagName('path') + g.getElementsByTagName('circle')
            group_id = g.attributes['id'].value
            if group_id != 'bg' and group_id != 'border':
                # print ('## ' + group_id + ':')
                for path in paths:
                    code = unicode(path.attributes['data-code'].value).encode("utf-8")
                    name = unicode(path.attributes['data-name'].value).encode("utf-8")
                    if code != '':
                        if code not in terms_by_id:
                            term = self.create_term(code, group_id, map_code, name)
                            data['terms'].append(term)
                            terms_by_id[code] = term
                            print('Term added: ' + name + ' ' + code)
                        elif (code in terms_by_id and
                                terms_by_id[code]['type'] != group_id):
                            code = code + '-' + group_id
                            term = self.create_term(code, group_id, map_code, name)
                            data['terms'].append(term)
                            terms_by_id[code] = term
                            print('Term added: ' + ' ' + code)
                        flashcard_id = map_code + '-' + code
                        if flashcard_id not in flashcards_by_id:
                            flashcard = {
                                'id': flashcard_id,
                                'term': code,
                                'context': map_code,
                                'description': code,
                            }
                            data['flashcards'].append(flashcard)
                            flashcards_by_id[flashcard_id] = flashcard
                            print('Flashcard added: ' + ' ' + code)
                        if map_code not in terms_by_id[code]['categories']:
                            terms_by_id[code]['categories'].append(map_code)

    def create_term(self, code, group_id, map_code, name):
        term = {
            'id': code,
            'type': group_id,
            'categories': [map_code],
        }
        if self.lang == 'all':
            languages = [l[0] for l in settings.LANGUAGES]
        else:
            languages = [self.lang]
        for lang in languages:
            term.update({
                'name-' + lang: name,
            })
        return term
