# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from geography.utils import QuestionService
from geography.models import Place, PlaceRelation, EloDifficulty, EloSkill
from random import random
from math import exp
from django.core.management import call_command
import geography.models.user
from django.db import connection
import logging

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<user\'s skill> <number of answers> [<code of the map>]'
    help = 'simulates answers for the user with the given skill'

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError(
                '''
                The command requires at least 2 arguments:
                    - user\'s skill
                    - number of answers
                ''')
        real_skill = float(args[0])
        number_of_answers = int(args[1])
        map_code = args[2] if len(args) > 2 else 'world'
        try:
            self.simulate(real_skill, number_of_answers, map_code)
        finally:
            self.clean()

    def simulate(self, real_skill, number_of_answers, map_code):
        map_place = PlaceRelation.objects.get(
            place__code=map_code,
            type=PlaceRelation.IS_ON_MAP)
        user = User(first_name='simulated', last_name='user')
        user.username = geography.models.user.get_unused_username(user)
        user.save()
        qs = QuestionService(user=user, map_place=map_place)
        for i in range(number_of_answers):
            question = qs.get_questions(1)[0]
            place = Place.objects.get(code=question['code'])
            difficulty = EloDifficulty.objects.get(place=place)
            number_of_options = float(str(question["type"][1:]))
            guess = 1.0 / number_of_options if number_of_options != 0 else 0
            probability = guess + (1 - guess) * (1.0 / (1 + exp(-real_skill + difficulty.value)))
            answer = {
                'code': question['code'],
                'type': question['type'],
                'place': question['place'],
                'response_time': 1000
            }
            if random() < probability:
                LOGGER.debug('correct answer simulated')
                answer['answer'] = question['code']
            else:
                LOGGER.debug('wrong answer simulated')
            qs.answer(answer)
        estimated_skill = EloSkill.objects.get(user=user)
        LOGGER.debug('estimated skill for the user %s is %s', str(user), estimated_skill.value)

    def clean(self):
        LOGGER.debug('started cleaning after simulation')
        cursor = connection.cursor()
        cursor.execute(
            '''
            DELETE FROM auth_user
            WHERE username LIKE \'simulateduser%%\'
            ''')
        call_command('clean_model')
        call_command('derived_elo_data')
        LOGGER.debug('cleaning after simulation finished')
