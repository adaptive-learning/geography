from proso_user.models import UserProfile
from django.core.management.base import BaseCommand
from optparse import make_option
from contextlib import closing
from django.db import connection
from clint.textui import progress
from django.db import transaction


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '--clean',
            action='store_true',
            dest='clean',
            default=False,
            help='Delete all previously loaded data'),
    )

    def handle(self, *args, **options):
        with transaction.atomic():
            if options['clean']:
                self.clean()
            self.create_profiles()

    def clean(self):
        with closing(connection.cursor()) as cursor:
            cursor.execute('TRUNCATE TABLE proso_user_userprofile')

    def create_profiles(self):
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                '''
                SELECT auth_user.id
                FROM auth_user
                LEFT JOIN lazysignup_lazyuser ON auth_user.id = lazysignup_lazyuser.user_id
                WHERE lazysignup_lazyuser.id IS NULL
               ''')
            for user_id, in progress.bar(cursor, every=max(1, cursor.rowcount / 100), expected_size=cursor.rowcount):
                UserProfile.objects.get_or_create(user_id=user_id, public=True)
