# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db import connection
from place import Place
import answer
import current
import prior


class KnowledgeUpdater:

    @staticmethod
    def on_answer_save(a, knowledge_retriever=None, in_memory=False):
        if not knowledge_retriever:
            if in_memory:
                knowledge_retriever = MemoryKnowledgeRetriever(a)
            else:
                knowledge_retriever = DatabaseKnowledgeRetriever(a)
        else:
            knowledge_retriever = knowledge_retriever.clone_with(a)
        if isinstance(a, answer.Answer):
            a = a.__dict__
        if knowledge_retriever.is_first_answer_for_user_place():
            prior_model = KnowledgeUpdater.get_prior_model()
            prior_skill = knowledge_retriever.prior_skill()
            difficulty = knowledge_retriever.difficulty()
            (prior_skill, difficulty) = prior_model(
                a,
                prior_skill,
                difficulty,
                knowledge_retriever)
            knowledge_retriever.prior_skill(prior_skill)
            knowledge_retriever.difficulty(difficulty)
        else:
            current_model = KnowledgeUpdater.get_current_model()
            current_skill = knowledge_retriever.current_skill()
            current_skill = current_model(
                a,
                current_skill,
                knowledge_retriever)
            knowledge_retriever.current_skill(current_skill)
        knowledge_retriever.update_numbers()
        return knowledge_retriever

    @staticmethod
    def get_prior_model():
        return prior.elo

    @staticmethod
    def get_current_model():
        return current.pfa


class MemoryKnowledgeRetriever:

    def __init__(self, a):
        if isinstance(a, answer.Answer):
            self.answer = a.__dict__
        else:
            self.answer = a
        self.first_place = {}
        self.first_user = {}
        self.both = {}
        self._difficulty = {}
        self._current_skill = {}
        self._prior_skill = {}

    def is_first_answer_for_user_place(self):
        return self.number_of_answers() == 0

    def number_of_first_answers_for_place(self):
        return self.first_place.get(self.answer['place_asked_id'], 0)

    def number_of_first_answers_for_user(self):
        return self.first_user.get(self.answer['user_id'], 0)

    def number_of_answers(self):
        return self.both.get((self.answer['place_asked_id'], self.answer['user_id']), 0)

    def clone_with(self, answer):
        copy = MemoryKnowledgeRetriever(answer)
        copy.first_user = self.first_user
        copy.first_place = self.first_place
        copy.both = self.both
        copy._difficulty = self._difficulty
        copy._prior_skill = self._prior_skill
        copy._current_skill = self._current_skill
        return copy

    def update_numbers(self):
        self.first_place[self.answer['place_asked_id']] = self.first_place.get(
            self.answer['place_asked_id'], 0) + 1
        self.first_user[self.answer['user_id']] = self.first_user.get(self.answer['user_id'], 0) + 1
        self.both[self.answer['place_asked_id'], self.answer['user_id']] = self.both.get((self.answer['place_asked_id'], self.answer['user_id']), 0) + 1

    def difficulty(self, new_value=None):
        if new_value:
            self._difficulty[self.answer['place_asked_id']] = new_value
        else:
            return self._difficulty.get(self.answer['place_asked_id'], 0.0)

    def prior_skill(self, new_value=None):
        if new_value:
            self._prior_skill[self.answer['user_id']] = new_value
        else:
            return self._prior_skill.get(self.answer['user_id'], 0.0)

    def current_skill(self, new_value=None):
        if new_value:
            self._current_skill[self.answer['place_asked_id'], self.answer['user_id']] = new_value
        else:
            return self._current_skill.get((self.answer['place_asked_id'], self.answer['user_id']), 0)

    def flush(self):
        cursor = connection.cursor()
        for user_id, skill in self._prior_skill.iteritems():
            cursor.execute(
                'INSERT INTO geography_priorskill (user_id, value) VALUES (%s, %s)',
                [user_id, skill])
        for place_id, difficulty in self._difficulty.iteritems():
            cursor.execute(
                'INSERT INTO geography_difficulty (place_id, value) VALUES (%s, %s)',
                [place_id, difficulty])
        for (place_id, user_id), skill in self._current_skill.iteritems():
            cursor.execute(
                'INSERT INTO geography_currentskill (user_id, place_id, value) VALUES (%s, %s, %s)',
                [user_id, place_id, skill])


class DatabaseKnowledgeRetriever:

    def __init__(self, answer):
        self.answer = answer
        self._difficulty = None
        self._prior_skill = None
        self._current_skill = None

    def is_first_answer_for_user_place(self):
        return not answer.Answer.objects.filter(
            user_id=self.answer.user_id,
            place_asked_id=self.answer.place_asked_id).exists()

    def number_of_first_answers_for_place(self):
        if not self._difficulty:
            self._difficulty = Difficulty.objects.from_place(answer.place_asked_id)
        return self._difficulty.get_num_of_answers()

    def number_of_first_answers_for_user(self):
        if not self._prior_skill:
            self._prior_skill = PriorSkill.objects.from_user(answer.user_id)
        return self._prior_skill.get_num_of_answers()

    def number_of_answers(self):
        if not self._current_skill:
            self._current_skill = CurrentSkill.objects.from_user_and_place(
                self.answer.user_id, self.answer.place_asked_id)
        return self._current_skill.get_num_of_answers()

    def clone_with(self, answer):
        return DatabaseKnowledgeRetriever(answer)

    def update_numbers(self):
        pass

    def difficulty(self, new_value=None):
        if not self._difficulty:
            self._difficulty = Difficulty.objects.from_place(self.answer.place_asked_id)
        if new_value:
            self._difficulty.value = new_value
            self._difficulty.save()
        else:
            return self._difficulty.value

    def prior_skill(self, new_value=None):
        if not self._prior_skill:
            self._prior_skill = PriorSkill.objects.from_user(self.answer.user_id)
        if new_value:
            self._prior_skill.value = new_value
            self._prior_skill.save()
        else:
            return self._prior_skill.value

    def current_skill(self, new_value=None):
        if not self._current_skill:
            self._current_skill = CurrentSkill.objects.from_user_and_place(
                self.answer.user_id, self.answer.place_asked_id)
        if new_value:
            self._current_skill.value = new_value
            self._current_skill.save()
        else:
            return self._current_skill.value

    def flush(self):
        pass


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
        cursor = connection.cursor()
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
        cursor = connection.cursor()
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
        cursor = connection.cursor()
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
