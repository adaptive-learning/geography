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
                " <flashcards-file> [<map-code>] [<map-type>] [<lang-code>]")
        map_code = None
        if len(args) > 1:
            map_code = args[1]
        map_type = 'state'
        if len(args) > 2:
            map_type = args[2]
        with open(args[0], 'r') as json_file:
            data = json.load(json_file, 'utf-8')
            data['contexts'] = data.get('contexts', [])
            data['terms'] = data.get('terms', [])
            data['categories'] = data.get('categories', [])
            data['flashcards'] = data.get('flashcards', [])
        if len(args) > 3:
            self.lang = args[3]
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
            if map_code not in contexts_by_id:
                self.add_context(data, map_code, map_type)
            else:
                self.disable_flashcards_on_context(data, map_code)
            self.add_map(map_code, data, terms_by_id)

        self.update_translations(data, terms_by_id, categories_by_id)
        # self.generate_translations_file(data)

        with open(options['output'], 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True)
            print(('Updated flashcards written to file: \'%s\'' %
                   options['output']))

    def disable_flashcards_on_context(self, data, map_code):
        for fc in data['flashcards']:
            if fc['context'] == map_code:
                fc['active'] = False

    def add_context(self, data, map_code, map_type):
        names = {}
        if self.lang == 'all':
            languages = [l[0] for l in settings.LANGUAGES]
        else:
            languages = [self.lang]
        for lang in languages:
            names[lang] = self.get_translation(map_code, lang)
        context = {
            'id': map_code,
        }
        category = {
            'id': map_code,
            'type': map_type,
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
                        else:
                            term = terms_by_id[code]
                            self.add_name(term, name)
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
                            print('Flashcard added: ' + name + ' ' + code)
                        else:
                            flashcard = flashcards_by_id[flashcard_id]
                            if 'active' in flashcard:
                                del flashcard['active']
                        if map_code not in terms_by_id[code]['categories']:
                            terms_by_id[code]['categories'].append(map_code)

    def create_term(self, code, group_id, map_code, name):
        term = {
            'id': code,
            'categories': [map_code, group_id],
        }
        self.add_name(term, name)
        return term

    def add_name(self, term, name):
        if self.lang == 'all':
            languages = [l[0] for l in settings.LANGUAGES]
        else:
            languages = [self.lang]
        for lang in languages:
            term.update({
                'name-' + lang: name,
            })
