# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from math import exp
from geography.models import Elo


class Command(BaseCommand):
    help = u'''Recompute derived data'''

    def handle(self, *args, **options):
        if len(args) > 0:
            raise CommandError('The command doesn\'t need any option.')
        self.load_derived_data()

    def load_derived_data(self):
        cursor = connection.cursor()
        # foreach answer update new datasets
        skills = {}
        local_skills = {}
        difficulties = {}
        cursor.execute('SELECT * FROM geography_answer')
        answer = self.fetchone(cursor)
        while answer:
            skill = skills.get(answer['user_id'], (0, 1))
            difficulty = difficulties.get(answer['place_asked_id'], (0, 1))
            local_skill = local_skills.get(
                (answer['user_id'], answer['place_asked_id']),
                ((skill[0] - difficulty[0]), 1))
            guess = 1.0 / answer['number_of_options'] if answer['number_of_options'] != 0 else 0
            prediction = self.predict(local_skill[0], guess)
            result = answer['place_asked_id'] == answer['place_answered_id']
            if local_skills.get((answer['user_id'], answer['place_asked_id']), None):
                skills[answer['user_id']] = (
                    skill[0] + Elo.alpha_fun(Elo.ALPHA_1, skill[1]) * (result - prediction),
                    skill[1] + 1
                )
                difficulties[answer['place_asked_id']] = (
                    difficulty[0] - Elo.alpha_fun(Elo.ALPHA_1, difficulty[1]) * (result - prediction),
                    difficulty[1] + 1
                )
            local_skills[(answer['user_id'], answer['place_asked_id'])] = (
                local_skill[0] + Elo.ALPHA_2 * (result - prediction),
                local_skill[1] + 1
            )
            answer = self.fetchone(cursor)
        # empty precomputed datasets
        cursor.execute('DELETE FROM geography_elodifficulty')
        cursor.execute('DELETE FROM geography_eloskill')
        cursor.execute('DELETE FROM geography_elolocalskill')
        # save new precomputed datasets
        for user_id, skill in skills.iteritems():
            cursor.execute(
                'INSERT INTO geography_eloskill (user_id, value) VALUES (%s, %s)',
                [user_id, skill[0]])
        for place_id, difficulty in difficulties.iteritems():
            cursor.execute(
                'INSERT INTO geography_elodifficulty (place_id, value) VALUES (%s, %s)',
                [place_id, difficulty[0]])
        for (user_id, place_id), local_skill in local_skills.iteritems():
            cursor.execute(
                'INSERT INTO geography_elolocalskill (user_id, place_id, value) VALUES (%s, %s, %s)',
                [user_id, place_id, local_skill[0]])

    def predict(self, local_skill, guess):
        return guess + (1 - guess) * (1.0 / (1 + exp(-local_skill)))

    def fetchone(self, cursor):
        fetched = cursor.fetchone()
        if fetched:
            return dict(zip([col[0] for col in cursor.description], fetched))
        else:
            return None
