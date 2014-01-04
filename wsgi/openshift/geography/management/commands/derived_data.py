# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from math import exp
from geography.models import Answer


class Command(BaseCommand):
    help = u'''Recompute derived data'''

    def handle(self, *args, **options):
        if len(args) > 0:
            raise CommandError('The command doesn\'t need any option.')
        self.load_derived_data()


    def load_derived_data(self):
        cursor = connection.cursor()
        # empty precomputed datasets
        cursor.execute('DELETE FROM geography_difficulty')
        cursor.execute('DELETE FROM geography_skill')
        cursor.execute('DELETE FROM geography_localskill')
        # foreach answer update new datasets
        skills = {}
        local_skills = {}
        difficulties = {}
        cursor.execute('SELECT * FROM geography_answer')
        answer = self.fetchone(cursor)
        while answer:
            skill = skills.get(answer['user_id'], 0)
            difficulty = difficulties.get(answer['place_asked_id'], 0)
            local_skill = local_skills.get(
                (answer['user_id'], answer['place_asked_id']),
                skill - difficulty)
            guess = 1.0/answer['number_of_options'] if answer['number_of_options'] != 0 else 0
            prediction = self.predict(local_skill, guess)
            result = answer['place_asked_id'] == answer['place_answered_id']
            if local_skills.get((answer['user_id'], answer['place_asked_id']), None):
                skills[answer['user_id']] = skill + Answer.objects.ALPHA_1 * (result - prediction)
                difficulties[answer['place_asked_id']] = difficulty - Answer.objects.ALPHA_1 * (result - prediction)
            local_skills[(answer['user_id'], answer['place_asked_id'])] = local_skill + Answer.objects.ALPHA_2 * (result - prediction)
            answer = self.fetchone(cursor)
        # save new precomputed datasets
        for user_id, skill in skills.iteritems():
            cursor.execute(
                'INSERT INTO geography_skill (user_id, value) VALUES (%s, %s)',
                [user_id, skill])
        for place_id, difficulty in difficulties.iteritems():
            cursor.execute(
                'INSERT INTO geography_difficulty (place_id, value) VALUES (%s, %s)',
                [place_id, difficulty])
        for (user_id, place_id), local_skill in local_skills.iteritems():
            cursor.execute(
                'INSERT INTO geography_localskill (user_id, place_id, value) VALUES (%s, %s, %s)',
                [user_id, place_id, local_skill])

    def predict(self, local_skill, guess):
        return guess + (1 - guess) * (1.0 / (1 + exp(-local_skill)))

    def fetchone(self, cursor):
        fetched = cursor.fetchone()
        if fetched:
            return dict(zip([col[0] for col in cursor.description], fetched))
        else:
            return None
