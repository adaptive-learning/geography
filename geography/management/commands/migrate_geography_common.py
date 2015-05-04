from django.core.management.base import BaseCommand
from django.core.management import call_command
from optparse import make_option


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '--geography-database',
            dest='geography_database',
            type=str,
            default='default',
            help='Database where the data for geogaphy app is.'),
        make_option(
            '--skip-auth',
            action='store_true',
            dest='skip_auth',
            default=False,
            help='Skip migration of auth data.'),
        make_option(
            '--skip-lazysignup',
            action='store_true',
            dest='skip_lazysignup',
            default=False,
            help='Skip migration of lazysignup data.'),
        make_option(
            '--skip-proso-feedback',
            action='store_true',
            dest='skip_proso_feedback',
            default=False,
            help='Skip migration of proso feedback data.'),
        make_option(
            '--skip-social-auth',
            action='store_true',
            dest='skip_social_auth',
            default=False,
            help='Skip migration of social auth data.'),
    )

    def handle(self, *args, **options):
        self.dump_load('auth', options, exclude=['auth.Permission', 'contenttypes'])
        self.dump_load('lazysignup', options)
        self.dump_load('proso_feedback', options)
        self.dump_load('social_auth', options)

    def dump_load(self, app, options, exclude=None):
        if exclude is None:
            exclude = []
        if not options['skip_' + app]:
            print ' -- migration of', app
            with open('geography-%s.json' % app, 'w') as output:
                call_command(
                    'dumpdata', app,
                    stdout=output,
                    exclude=exclude,
                    database=options['geography_database'])
            call_command('loaddata', 'geography-%s.json' % app)
        else:
            print ' -- skipping migration of', app
