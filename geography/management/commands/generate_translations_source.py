from django.core.management.base import BaseCommand, CommandError
import json
from django.conf import settings
import codecs


class Command(BaseCommand):
    MAPS_DIR = 'geography/static/map'
    option_list = BaseCommand.option_list + (
    )

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError(
                "Not enough arguments. One argument required: " +
                " <flashcards-file>")
        with open(args[0], 'r') as json_file:
            data = json.load(json_file, 'utf-8')

        self.generate_translations_file(data)

    def generate_translations_file(self, data):
        for lang in [(settings.LANGUAGE_CODE,)]:
            file_name = 'data/translations_%s.csv' % lang[0]
            with codecs.open(file_name, 'w', encoding='utf-8') as f:
                for category in data['categories']:
                    row = u'"%s","%s"\n' % (category['id'], category.get(
                        'name-' + lang[0], ''))
                    f.write(row)
                for term in data['terms']:
                    if '-by-' not in term['id']:
                        name = unicode(term.get('name-' + lang[0], ''))
                        row = u'"%s","%s"\n' % (term['id'], name)
                        f.write(row)
