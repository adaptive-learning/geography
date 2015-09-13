from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import json
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
        if len(args) < 3:
            raise CommandError(
                "Not enough arguments. Three arguments required: " +
                " <flashcards-file> <lang-code> <translations-file>")
        translations = self.get_translations(args[2])
        lang = args[1]
        with open(args[0], 'r') as json_file:
            data = json.load(json_file, 'utf-8')
            for c in data['contexts']:
                if c['id'] in translations:
                    c['name-' + lang] = translations[c['id']]
                    c['content-' + lang] = c['content-en']
                else:
                    print ('Warning: missing translation for context %s' %
                           c['name-en'])
            for t in data['terms']:
                if t['id'] in translations:
                    t['name-' + lang] = translations[t['id']]
                else:
                    t['name-' + lang] = t['name-en']
                    print ('Warning: missing translation for term ' +
                           '\'%s\', id: \'%s\'' % (t['name-en'], t['id']))
            for c in data['categories']:
                if c['id'] in translations:
                    c['name-' + lang] = translations[c['id']]
                else:
                    print ('Warning: missing translation for category ' +
                           '\'%s\', id: \'%s\'' % (c['name-en'], c['id']))
        with open(options['output'], 'w') as f:
            json.dump(data, f, indent=2)
            print ('Updated flashcards written to file: \'%s\'' %
                   options['output'])

    def get_translations(self, filename):
        translations = {}
        with open(filename, 'r') as csvfile:
            translations_reader = csv.reader(csvfile, delimiter='\t')
            for row in translations_reader:
                if len(row) == 2:
                    translations[row[0]] = row[1]
        return translations
