# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from geography.models import Group


class Command(BaseCommand):

    def handle(self, *args, **options):
        values = []
        (group_name, default_value) = args[0].split('=')
        prob_value_pairs = args[1:]
        for arg in prob_value_pairs:
            (value, probability) = arg.split('=')
            probability = int(probability.strip())
            value = value.strip()
            values.append((probability, value))
        Group.objects.init_group(group_name, default_value, values)
