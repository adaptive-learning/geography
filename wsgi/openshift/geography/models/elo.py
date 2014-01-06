# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db import connection
from datetime import datetime
from math import exp
import math
import answer
import logging
import place
LOGGER = logging.getLogger(__name__)


class Elo:

    ALPHA_1 = 0.4
    ALPHA_2 = 1.2

    @staticmethod
    def predict(user, place, guess=0):
        skill = EloLocalSkill.objects.from_user_and_place(user, place)
        return guess + (1 - guess) * (1.0 / (1 + exp(-skill.value)))

    @staticmethod
    def on_answer_save(answer):
        g = 1.0 / answer.number_of_options if answer.number_of_options != 0 else 0
        prediction = Elo.predict(answer.user, answer.place_asked, g)
        result = answer.place_asked == answer.place_answered
        Elo.update_model(answer.user, answer.place_asked, prediction, result)

    @staticmethod
    def update_model(user, place, prediction, result):
        if not answer.Answer.objects.filter(user=user, place_asked=place).exists():
            LOGGER.debug(
                "new local skill for user %s and place %s",
                str(user), str(place))
            skill = EloSkill.objects.from_user(user)
            skill_new = skill.value + Elo.ALPHA_1 * (result - prediction)
            LOGGER.debug(
                "updating skill for user %s, from %s to %s",
                str(user), str(skill.value), str(skill_new))
            skill.value = skill_new
            skill.save()
            difficulty = EloDifficulty.objects.from_place(place)
            difficulty_new = difficulty.value - Elo.ALPHA_1 * (result - prediction)
            LOGGER.debug(
                "updating difficulty for place %s, from %s to %s",
                str(place),
                str(difficulty.value),
                str(difficulty_new))
            difficulty.value = difficulty_new
            difficulty.save()
        else:
            local_skill = EloLocalSkill.objects.from_user_and_place(user, place)
            local_skill_new = local_skill.value + Elo.ALPHA_2 * (result - prediction)
            LOGGER.debug(
                "updating local skill for user %s and place %s, from %s to %s",
                str(user), str(place), str(local_skill.value), str(local_skill_new))
            local_skill.value = local_skill_new
            local_skill.save()

    @staticmethod
    def get_places_to_ask(user, map_place, expected_probability, n):
        expected_skill = - math.log((1 - expected_probability) / expected_probability)
        cursor = connection.cursor()
        cursor.execute(
            '''
            SELECT
                geography_place.*,
                geography_elolocalskill_prepared.value as local_skill,
                (
                    ABS(geography_elolocalskill_prepared.value - %s)
                    /
                    ABS(%s + SIGN(geography_elolocalskill_prepared.value - %s) * 5)
                ) AS deviation,
                COUNT(geography_answer.id) AS number_of_answers,
                CASE
                    WHEN COALESCE(MIN(
                            UNIX_TIMESTAMP(\'''' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '''\')
                            -
                            UNIX_TIMESTAMP(geography_answer.inserted)
                        ) / 60, 10) > 1 THEN 0
                    ELSE 1
                END AS invalidity
            FROM
                geography_elolocalskill_prepared
                LEFT JOIN geography_place
                    ON geography_place.id = geography_elolocalskill_prepared.place_id
                LEFT JOIN geography_answer
                    ON geography_answer.user_id = geography_elolocalskill_prepared.user_id
                    AND geography_answer.place_asked_id = place_id
            WHERE
                geography_place.id IN (
                    SELECT
                        geography_placerelation_related_places.place_id
                    FROM
                        geography_placerelation
                        INNER JOIN geography_placerelation_related_places
                            ON placerelation_id = geography_placerelation.id
                    WHERE
                        geography_placerelation.place_id = %s
                        AND
                        geography_placerelation.type = %s
                )
                AND geography_elolocalskill_prepared.user_id = %s
            GROUP BY
                geography_elolocalskill_prepared.user_id, geography_elolocalskill_prepared.place_id
            ORDER BY invalidity, deviation, RAND() ASC
            LIMIT %s;
            ''',
            [
                float(expected_skill),
                float(expected_skill),
                float(expected_skill),
                int(map_place.place.id),
                int(place.PlaceRelation.IS_ON_MAP),
                int(user.id),
                int(n)
            ]
        )
        dict_places = Elo.fetchall(cursor)
        return [
            (
                place.Place(id=d['id'], code=d['code'], name=d['name'], type=d['type']),
                1.0 / (1 + exp(-d['local_skill'])),
                d['number_of_answers']
            )
            for d in dict_places
        ]

    @staticmethod
    def fetchall(cursor):
        "Returns all rows from a cursor as a dict"
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]


class EloLocalSkillManager(models.Manager):

    def from_user_and_place(self, user, place):
        try:
            return EloLocalSkill.objects.get(user=user, place=place)
        except EloLocalSkill.DoesNotExist:
            try:
                difficulty = EloDifficulty.objects.from_place(place).value
            except EloDifficulty.DoesNotExist:
                difficulty = 0
            try:
                skill = EloSkill.objects.from_user(user).value
                local_skill = skill - difficulty
            except EloSkill.DoesNotExist:
                local_skill = 0
        return EloLocalSkill(
            value=local_skill,
            user=user,
            place=place)


class EloLocalSkill(models.Model):

    value = models.FloatField(default=0)
    user = models.ForeignKey(User)
    place = models.ForeignKey(place.Place)
    objects = EloLocalSkillManager()

    class Meta:
        app_label = 'geography'


class EloDifficultyManager(models.Manager):

    def from_place(self, place):
        try:
            return EloDifficulty.objects.get(place=place)
        except EloDifficulty.DoesNotExist:
            return EloDifficulty(place=place)


class EloDifficulty(models.Model):

    value = models.FloatField(default=0)
    place = models.ForeignKey(place.Place)
    objects = EloDifficultyManager()

    class Meta:
        app_label = 'geography'


class EloSkillManager(models.Manager):

    def from_user(self, user):
        try:
            return EloSkill.objects.get(user=user)
        except EloSkill.DoesNotExist:
            return EloSkill(user=user)


class EloSkill(models.Model):

    value = models.FloatField(default=0)
    user = models.ForeignKey(User)
    objects = EloSkillManager()

    class Meta:
        app_label = 'geography'
