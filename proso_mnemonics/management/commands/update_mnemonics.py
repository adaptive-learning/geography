# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from proso_mnemonics.models import Mnemonic
from geography.models import Place
import csv
import settings
import os.path


class Command(BaseCommand):
    help = """Add new places"""

    def handle(self, *args, **options):
        for lang in settings.LANGUAGES:
            self.set_mnemonics(lang[0])

    def set_mnemonics(self, lang_code):
        mnemonics = self.get_mnemonics(lang_code)
        for code, text in mnemonics:
            try:
                place = Place.objects.get(code=code)
            except Place.DoesNotExist:
                print("Warning: bad place code: " + code)
                continue
            try:
                m = Mnemonic.objects.get(
                    place=place,
                    language=Mnemonic.LANGUAGES_REVERSE[lang_code],
                )
            except Mnemonic.DoesNotExist:
                m = Mnemonic(
                    place=place,
                    language=Mnemonic.LANGUAGES_REVERSE[lang_code],
                )
            if m.text != text.decode('utf-8'):
                m.text = text
                m.save()

    def get_mnemonics(self, lang_code):
        mnemonics = []
        fname = settings.PROJECT_DIR + '/mnemonics_' + lang_code + '.csv'
        if os.path.isfile(fname):
            with open(fname, 'rb') as csvfile:
                mnemonics_reader = csv.reader(csvfile, delimiter='\t')
                for row in mnemonics_reader:
                    if len(row) == 2 and row[1] != '':
                        mnemonics.append(row)
        else:
            print("Warning: file not found: '%s'" % fname)
        return mnemonics
