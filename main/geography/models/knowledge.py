# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db import connection
from place import Place
from proso.geography.environment import Environment, InMemoryEnvironment
from proso.geography.model import AnswerStream
from proso.geography.prior import elo_prepare, elo_predict, elo_update
from proso.geography.current import pfa_prepare, pfa_predict, pfa_update
from contextlib import closing
from django.core.cache import cache
import hashlib
import json


class KnowledgeUpdater(AnswerStream):

    def __init__(self, environment):
        self._environment = environment

    def current_prepare(self, answer, env):
        return pfa_prepare(answer, env)

    def current_predict(self, answer, data):
        return pfa_predict(answer, data)

    def current_update(self, answer, env, data, prediction):
        return pfa_update(answer, env, data, prediction)

    def environment(self):
        return self._environment

    def prior_prepare(self, answer, env):
        return elo_prepare(answer, env)

    def prior_predict(self, answer, data):
        return elo_predict(answer, data)

    def prior_update(self, answer, env, data, prediction):
        return elo_update(answer, env, data, prediction)


class DatabaseEnvironment(Environment):

    USER = 1
    PLACE = 2
    USER_PLACE = 3

    def answers_num(self, user_id=None, place_id=None):
        return self.answers_nums([user_id], [place_id])[0]

    def answers_nums(self, user_ids, place_ids):
        with closing(connection.cursor()) as cursor:
            args_type = self._args_type(user_ids, place_ids)
            if args_type == DatabaseEnvironment.USER:
                cursor.execute(
                    '''
                    SELECT
                        user_id,
                        COUNT(geography_answer.id)
                    FROM geography_answer
                    WHERE user_id IN (''' + ','.join([str(i) for i in user_ids]) + ''')
                    GROUP BY user_id
                    ''')
                found = dict(cursor.fetchall())
                return map(lambda i: found[i], user_ids)
            elif args_type == DatabaseEnvironment.PLACE:
                cursor.execute(
                    '''
                    SELECT
                        place_asked_id,
                        COUNT(geography_answer.id)
                    FROM geography_answer
                    WHERE place_asked_id IN (''' + ','.join([str(i) for i in place_ids]) + ''')
                    GROUP BY place_asked_id
                    ''')
                found = dict(cursor.fetchall())
                return map(lambda i: found[i], place_ids)
            else:
                cursor.execute(
                    '''
                    SELECT
                        user_id,
                        place_asked_id,
                        COUNT(geography_answer.id)
                    FROM geography_answer
                    WHERE user_id IN (''' + ','.join([str(i) for i in user_ids]) + ''')
                    AND place_asked_id IN (''' + ','.join([str(i) for i in place_ids]) + ''')
                    GROUP BY user_id, place_asked_id
                    ''')
                found = dict(map(lambda (i, j, k): ((i, j), k), cursor.fetchall()))
                return map(lambda i: found.get(i, 0), zip(user_ids, place_ids))

    def confused_index(self, place_id, place_ids):
        cache_key = (
            'confused_index_' +
            hashlib.sha1(str(place_id)).hexdigest() +
            '_' +
            hashlib.sha1(str(place_ids)).hexdigest())
        places_json = cache.get(cache_key)
        if places_json is None:
            with closing(connection.cursor()) as cursor:
                cursor.execute(
                    '''
                    SELECT
                        geography_place.id,
                        COUNT(geography_answer.id) AS confusing_factor
                    FROM
                        geography_place
                        LEFT JOIN geography_answer ON (
                            geography_answer.place_answered_id = geography_place.id
                            AND geography_answer.place_asked_id = %s)
                    WHERE
                        geography_place.id IN (''' + ','.join([str(i) for i in place_ids]) + ''')
                        AND
                        geography_answer.place_asked_id != geography_answer.place_answered_id
                    GROUP BY geography_place.id
                    ''', [place_id])
                confusing_factor = dict([(p[0], p[1]) for p in cursor.fetchall()])
                json_places = json.dumps(map(lambda i: confusing_factor.get(i, 0), place_ids))
            place_answered_num = self.answers_num(place_id=place_id)
            expire_hours = max(1, int(round(place_answered_num / 100.0)))
            expire_seconds = 60 * 60 * expire_hours
            cache.set(cache_key, json_places, expire_seconds)
            places_json = cache.get(cache_key)
        return json.loads(places_json)

    def current_skill(self, user_id, place_id, new_value):
        if new_value is not None:
            skill = CurrentSkill.objects.from_user_and_place(user_id, place_id)
            skill.value = new_value
            skill.save()
        else:
            return self.current_skills([user_id], [place_id])[0]

    def current_skills(self, user_ids, place_ids):
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                '''
                SELECT
                    user_id,
                    place_id,
                    value
                FROM geography_currentskill_prepared
                WHERE user_id IN (''' + ','.join([str(i) for i in user_ids]) + ''')
                AND place_id IN (''' + ','.join([str(i) for i in place_ids]) + ''')
                ''')
            current_skills = dict(map(lambda (i, j, k): ((i, j), k), cursor.fetchall()))
            return map(lambda k: current_skills.get(k, 0), zip(user_ids, place_ids))

    def difficulty(self, place_id, new_value=None):
        if new_value:
            difficulty = Difficulty.objects.from_place(place_id)
            difficulty.value = new_value
            difficulty.save()
        else:
            return self.difficulties([place_id])

    def difficulties(self, place_ids):
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                '''
                SELECT
                    place_id,
                    value
                FROM geography_difficulty
                WHERE place_id IN (''' + ','.join([str(i) for i in place_ids]) + ''')
                ''')
            found = dict(cursor.fetchall())
            return map(lambda i: found.get(i, 0), place_ids)

    def first_answers_num(self, user_id=None, place_id=None):
        return self.first_answers_nums([user_id], [place_id])[0]

    def first_answers_nums(self, user_ids, place_ids):
        with closing(connection.cursor()) as cursor:
            args_type = self._args_type(user_ids, place_ids)
            if args_type == DatabaseEnvironment.USER:
                cursor.execute(
                    '''
                    SELECT
                        user_id,
                        COUNT(DISTINCT(place_asked_id))
                    FROM geography_answer
                    WHERE user_id IN (''' + ','.join([str(i) for i in user_ids]) + ''')
                    GROUP BY user_id
                    ''')
                found = dict(cursor.fetchall())
                return map(lambda i: found[i], user_ids)
            elif args_type == DatabaseEnvironment.PLACE:
                cursor.execute(
                    '''
                    SELECT
                        place_asked_id,
                        COUNT(DISTINCT(place_asked_id))
                    FROM geography_answer
                    WHERE place_asked_id IN (''' + ','.join([str(i) for i in place_ids]) + ''')
                    GROUP BY place_asked_id
                    ''')
                found = dict(cursor.fetchall())
                return map(lambda i: found[i], place_ids)
            else:
                cursor.execute(
                    '''
                    SELECT
                        user_id,
                        place_asked_id,
                        1
                    FROM geography_answer
                    WHERE user_id IN (''' + ','.join([str(i) for i in user_ids]) + ''')
                    AND place_asked_id IN (''' + ','.join([str(i) for i in place_ids]) + ''')
                    GROUP BY user_id, place_asked_id
                    ''')
                found = dict(map(lambda (i, j, k): ((i, j), k), cursor.fetchall()))
                return map(lambda i: found.get(i, 0), zip(user_ids, place_ids))

    def has_answer(self, user_id=None, place_id=None):
        return self.first_answers_num(user_id=user_id, place_id=place_id) > 0

    def have_answer(self, user_ids=None, place_ids=None):
        return map(
            lambda x: x > 0,
            self.first_answers_nums(user_ids, place_ids))

    def last_time(self, user_id=None, place_id=None):
        return self.last_times([user_id], [place_id])[0]

    def last_times(self, user_ids, place_ids):
        with closing(connection.cursor()) as cursor:
            args_type = self._args_type(user_ids, place_ids)
            if args_type == DatabaseEnvironment.USER:
                cursor.execute(
                    '''
                    SELECT
                        user_id,
                        max(inserted)
                    FROM geography_answer
                    WHERE user_id IN (''' + ','.join([str(i) for i in user_ids]) + ''')
                    GROUP BY user_id
                    ''')
                found = dict(cursor.fetchall())
                print 'A', found
                return map(lambda i: found[i], user_ids)
            elif args_type == DatabaseEnvironment.PLACE:
                cursor.execute(
                    '''
                    SELECT
                        place_asked_id,
                        MAX(inserted)
                    FROM geography_answer
                    WHERE place_asked_id IN (''' + ','.join([str(i) for i in place_ids]) + ''')
                    GROUP BY place_asked_id
                    ''')
                found = dict(cursor.fetchall())
                print 'B', found
                return map(lambda i: found[i], place_ids)
            else:
                cursor.execute(
                    '''
                    SELECT
                        user_id,
                        place_asked_id,
                        MAX(inserted)
                    FROM geography_answer
                    WHERE user_id IN (''' + ','.join([str(i) for i in user_ids]) + ''')
                    AND place_asked_id IN (''' + ','.join([str(i) for i in place_ids]) + ''')
                    GROUP BY user_id, place_asked_id
                    ''')
                found = dict(map(lambda (i, j, k): ((i, j), k), cursor.fetchall()))
                return map(lambda i: found.get(i, None), zip(user_ids, place_ids))

    def prior_skill(self, user_id, new_value=None):
        if new_value is not None:
            prior_skill = PriorSkill.objects.from_user(user_id)
            prior_skill.value = new_value
            prior_skill.save()
        else:
            return self.prior_skills([user_id])[0]

    def prior_skills(self, user_ids):
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                '''
                SELECT
                    user_id,
                    value
                FROM geography_priorskill_prepared
                WHERE user_id IN (''' + ','.join([str(i) for i in user_ids]) + ''')
                ''')
            found = dict(cursor.fetchall())
            return map(lambda user_id: found[user_id], user_ids)

    def process_answer(self, user_id, place_asked_id, place_answered_id, inserted):
        pass

    def rolling_success(self, user_id, n=10):
        if n == 0:
            return 1.0
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                '''
                SELECT
                    place_asked_id,
                    place_answered_id
                FROM
                    geography_answer
                WHERE
                    user_id = %s
                ORDER BY id DESC
                LIMIT %s
                ''', [user_id, n])
            all_answered = cursor.fetchall()
            return sum([r[0] == r[1] for r in all_answered]) / min(float(n), max(1.0, float(len(all_answered))))

    def _args_type(self, user_ids, place_ids):
        user_ids_nones = [id is None for id in user_ids]
        place_ids_nones = [id is None for id in place_ids]
        if any(user_ids_nones) and not all(user_ids_nones):
            raise Exception('no or all user ids have to specified')
        if any(place_ids_nones) and not all(place_ids_nones):
            raise Exception('no or all user ids have to specified')
        if all(user_ids_nones) and all(place_ids_nones):
            raise Exception('ether user ids or place ids have to specified')
        if any(place_ids_nones):
            return DatabaseEnvironment.USER
        if any(user_ids_nones):
            return DatabaseEnvironment.PLACE
        return DatabaseEnvironment.USER_PLACE


class InMemoryEnvironmentWithFlush(InMemoryEnvironment):

    def flush_all(self, prior_skill, current_skill, difficulty):
        sql = '''INSERT INTO geography_priorskill (user_id, value)
                VALUES ''' + ','.join(self._prior_skill_values()) + ';'
        sql += '''
                INSERT INTO geography_difficulty (place_id, value)
                VALUES''' + ','.join(self._difficulty_values()) + ';'
        sql += '''
                INSERT INTO geography_currentskill (user_id, place_id, value)
                VALUES ''' + ','.join(self._current_skill_values()) + ';'
        return sql

    def _difficulty_values(self):
        return [
            '({}, {})'.format(place_id, difficulty)
            for place_id, difficulty in self._difficulty.iteritems()
        ]

    def _prior_skill_values(self):
        return [
            '({}, {})'.format(user_id, skill)
            for user_id, skill in self._prior_skill.iteritems()
        ]

    def _current_skill_values(self):
        return [
            '({}, {}, {})'.format(user_id, place_id, skill)
            for (user_id, place_id), skill in self._current_skill.iteritems()
        ]


class DifficultyManager(models.Manager):

    def from_place(self, place):
        try:
            if isinstance(place, Place):
                place = place.id
            return Difficulty.objects.get(place_id=place)
        except Difficulty.DoesNotExist:
            return Difficulty(place_id=place)


class Difficulty(models.Model):

    value = models.FloatField(default=0)
    place = models.ForeignKey(Place, unique=True)
    objects = DifficultyManager()

    def get_num_of_answers(self):
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                '''
                SELECT COUNT(DISTINCT(user_id))
                FROM geography_answer
                WHERE place_asked_id = %s
                ''',
                [int(self.place_id)]
            )
            return cursor.fetchone()[0]

    class Meta:
        app_label = 'geography'


class PriorSkillManager(models.Manager):

    def from_user(self, user):
        try:
            if isinstance(user, User):
                user = user.id
            return PriorSkill.objects.get(user_id=user)
        except PriorSkill.DoesNotExist:
            return PriorSkill(user_id=user)


class PriorSkill(models.Model):

    value = models.FloatField(default=0)
    user = models.ForeignKey(User, unique=True)
    objects = PriorSkillManager()

    def get_num_of_answers(self):
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                '''
                SELECT COUNT(DISTINCT(place_asked_id))
                FROM geography_answer
                WHERE user_id = %s
                ''',
                [int(self.user_id)]
            )
            return cursor.fetchone()[0]

    class Meta:
        app_label = 'geography'


class CurrentSkillManager(models.Manager):

    def from_user_and_place(self, user, place):
        try:
            if isinstance(user, User):
                user = user.id
            if isinstance(place, Place):
                place = place.id
            return CurrentSkill.objects.get(user=user, place=place)
        except CurrentSkill.DoesNotExist:
            try:
                difficulty = Difficulty.objects.from_place(place).value
            except Difficulty.DoesNotExist:
                difficulty = 0
            try:
                skill = PriorSkill.objects.from_user(user).value
                local_skill = skill - difficulty
            except PriorSkill.DoesNotExist:
                local_skill = 0
        return CurrentSkill(
            value=local_skill,
            user_id=user,
            place_id=place)


class CurrentSkill(models.Model):

    value = models.FloatField(default=0)
    user = models.ForeignKey(User)
    place = models.ForeignKey(Place)
    objects = CurrentSkillManager()

    def get_num_of_answers(self):
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                '''
                SELECT COUNT(id)
                FROM geography_answer
                WHERE
                    place_asked_id = %s
                    AND
                    user_id = %s
                ''',
                [int(self.place_id), int(self.user_id)]
            )
            return cursor.fetchone()[0]

    class Meta:
        app_label = 'geography'
        unique_together = ('user', 'place')
