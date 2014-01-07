# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from geography.models import Answer
import csv


class Command(BaseCommand):
    help = 'dump model to csv file'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError(
                '''
                The command requires exactly one argument:
                    - destination file
                ''')
        self.dump_queryset(
            Answer.objects.all(),
            args[0],
            user='user_id',
            place_asked='place_asked_id',
            place_answered='place_answered_id')

    def dump_queryset(self, qs, dest_file, **field_mapping):
        model = qs.model
        headers = [field.name for field in model._meta.fields]
        with open(dest_file, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            for obj in qs.iterator():
                row = [self.getattr(obj, field, field_mapping) for field in headers]
                writer.writerow(row)

    def getattr(self, obj, field, field_mapping):
        if field_mapping.get(field, None):
            field = field_mapping.get(field)
        val = getattr(obj, field)
        if callable(val):
            val = val()
        if type(val) == unicode:
            val = val.encode('utf-8')
        return val
