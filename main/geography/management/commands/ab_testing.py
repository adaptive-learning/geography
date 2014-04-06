# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from geography.models import Group
from optparse import make_option
from prettytable import PrettyTable


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '--command-help',
            action='store_true',
            dest='command_help',
            help='shows helps for the given command',
        ),
        make_option(
            '--max-answers',
            type='int',
            action='store',
            dest='max_answers',
            help='maximum number of answers of user allowed to be in A/B testing group',
        ),
        make_option(
            '--min-answers',
            type='int',
            action='store',
            dest='min_answers',
            help='minimum number of answers of user allowed to be in A/B testing group',
        ),
    )

    args = '<command> [command arguments]'

    help = '''
    ----------------------------------------------------------------------------
    command for manipulation with A/B testing groups and values

    the following subcommands are available
        * disable
        * enable
        * init
        * overview
        * stats-user
        * stats-answer

    to print more help use the following command:

        ./manage.py ab_testing <command> --comand-help
    ----------------------------------------------------------------------------
            '''

    def handle(self, *args, **options):
        if not len(args):
            raise CommandError(Command.help)
        command = args[0]
        command_args = args[1:]
        if command == 'disable':
            return self.enable_disable(command_args, options, False)
        elif command == 'enable':
            return self.enable_disable(command_args, options, True)
        elif command == 'init':
            return self.init(command_args, options)
        elif command == 'overview':
            return self.overview(command_args, options)
        elif command == 'stats-user':
            return self.stats_user(command_args, options)
        elif command == 'stats-answer':
            return self.stats_answer(command_args, options)
        else:
            raise CommandError('unknow command: ' + command)

    def enable_disable(self, args, options, active):
        if options.get('command_help', False):
            print self.help_enable_disable()
            return
        group_name = args[0]
        group = Group.objects.get(name=group_name)
        group.active = active
        group.save()

    def init(self, args, options):
        if options.get('command_help', False):
            print self.help_init()
            return
        values = []
        (group_name, default_value) = args[0].split('=')
        prob_value_pairs = args[1:]
        for arg in prob_value_pairs:
            (value, probability) = arg.split('=')
            probability = int(probability.strip())
            value = value.strip()
            values.append((probability, value))
        Group.objects.init_group(
            group_name,
            default_value,
            values,
            max_answers=options.get('max_answers') if options.get('max_answers') else 0,
            min_answers=options.get('min_answers') if options.get('min_answers') else 0)

    def overview(self, args, options):
        if options.get('command_help', False):
            print self.help_overview()
            return
        groups = Group.objects.all().order_by('name')
        table = PrettyTable(['Group', 'Active'])
        table.align['Group'] = 'l'
        for g in groups:
            table.add_row([g.name, g.active])
        print table

    def stats_user(self, args, options):
        if options.get('command_help', False):
            print self.help_stats_user()
            return
        group_name = args[0]
        users_per_value = Group.objects.users_per_value(group_name)
        table = PrettyTable(['Value', 'Number of users'])
        table.align['Value'] = 'l'
        for k, v in users_per_value.iteritems():
            table.add_row([k, v])
        print table.get_string(sort_by='Value')

    def stats_answer(self, args, options):
        if options.get('command_help', False):
            print self.help_stats_answer()
            return
        group_name = args[0]
        answers_per_value = Group.objects.answers_per_value(group_name)
        table = PrettyTable(['Value', 'Number of answers'])
        table.align['Value'] = 'l'
        for k, v in answers_per_value.iteritems():
            table.add_row([k, v])
        print table.get_string(sort_by='Value')

    def help_enable_disable(self):
            return '''
        enable/disable the given group

            ./manage.py ab_testing [enable|disable] <group name>
                    '''

    def help_init(self):
        return '''
    initilize a new A/B testing group with its values

        ./manage.py ab_testing init <group name>=<default value> [<value>=<percentige>]
                '''

    def help_stats_user(self):
        return '''
    show number of users for the values of the given group

        ./manage.py ab_testing stats-user <group name>
                '''

    def help_stats_answer(self):
            return '''
        show number of answers for the values of the given group

            ./manage.py ab_testing stats-answer <group name>
                    '''
