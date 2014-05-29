# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from geography.models import PlaceRelation, Test


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '--command-help',
            action='store_true',
            dest='command_help',
            help='shows helps for the given command',
        ),
        make_option(
            '--test-size',
            type='int',
            action='store',
            dest='test_size',
            default=10,
            help='number of answers in one test',
        ),
        make_option(
            '--map-code',
            type='str',
            action='store',
            dest='map_code',
            help='code of the map where the testing is applied',
        ),
        make_option(
            '--place-type',
            type='int',
            action='store',
            dest='place_type',
            help='type of the place where the testing is applied',
        ),
    )

    args = '<command>'

    help = '''
    ----------------------------------------------------------------------------
    command for manipulation with testing

    the following subcommands are available:
        * init

    to print more help use the following command:

        ./manage.py testing <command> --command-help
    ----------------------------------------------------------------------------
    '''

    def handle(self, *args, **options):
        if not len(args):
            raise CommandError(Command.help)
        command = args[0]
        command_args = args[1:]
        if command == 'init':
            return self.init(command_args, options)
        else:
            raise CommandError('unknow command: ' + command)

    def init(self, args, options):
        if options.get('command_help', False):
            print self.help_init()
            return
        map_code = options.get('map_code')
        if map_code is None:
            raise CommandError('map code has to be specified')
        place_type = options.get('place_type')
        if place_type is None:
            raise CommandError('place type has to be specified')
        test_size = options.get('test_size')
        map_place = PlaceRelation.objects.get(
            place__code=map_code,
            type=PlaceRelation.IS_ON_MAP)
        tests = Test.objects.init(map_place, place_type, test_size)
        print 'number of created tests:', len(tests)
        for t in tests:
            print 'test:'
            for p in t:
                print "\t", p

    def help_init(self):
        return '''
    initilize a testing

        ./manage.py testing init --map-code=<code> --test-size=<int> --place-type=<int>
                '''
