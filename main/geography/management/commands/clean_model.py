# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from django.db import connection


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        cursor = connection.cursor()
        cursor.execute(
            '''
            DELETE FROM geography_answer
            WHERE user_id NOT IN
                (SELECT id FROM auth_user)
            ''')
