# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models
from place import Place
from skill import LocalSkill, Skill, Difficulty
from math import exp
from django.contrib.auth.models import User
import logging
LOGGER = logging.getLogger(__name__)


class AnswerManager(models.Manager):

    ALPHA_1 = 0.4
    ALPHA_2 = 1.2

    def get_last_10_answers(self, user):
        return self.filter(
            user=user,
        ).order_by("-inserted")[:10]

    # Elo Model
    def predict(self, user, place, guess=0):
        skill = LocalSkill.objects.from_user_and_place(user, place)
        return guess + (1 - guess) * (1.0 / (1 + exp(-skill.value)))

    def update_model(self, user, place, prediction, result):
        if not Answer.objects.filter(user=user, place_asked=place).exists():
            LOGGER.debug(
                "new local skill for user %s and place %s",
                str(user), str(place))
            skill = Skill.objects.from_user(user)
            skill_new = skill.value + self.ALPHA_1 * (result - prediction)
            LOGGER.debug(
                "updating skill for user %s, from %s to %s",
                str(user), str(skill.value), str(skill_new))
            skill.value = skill_new
            skill.save()
            difficulty = Difficulty.objects.from_place(place)
            difficulty_new = difficulty.value - self.ALPHA_1 * (result - prediction)
            LOGGER.debug(
                "updating difficulty for place %s, from %s to %s",
                str(place),
                str(difficulty.value),
                str(difficulty_new))
            difficulty.value = difficulty_new
            difficulty.save()
        else:
            local_skill = LocalSkill.objects.from_user_and_place(user, place)
            local_skill_new = local_skill.value + self.ALPHA_2 * (result - prediction)
            LOGGER.debug(
                "updating local skill for user %s and place %s, from %s to %s",
                str(user), str(place), str(local_skill.value), str(local_skill_new))
            local_skill.value = local_skill_new
            local_skill.save()


class Answer(models.Model):
    FIND_ON_MAP = 1
    PICK_NAME = 2
    QUESTION_TYPES = (
        (FIND_ON_MAP, "find on map"),
        (PICK_NAME, "pick name")
    )
    user = models.ForeignKey(User)
    place_asked = models.ForeignKey(Place, related_name='place_asked_id')
    place_answered = models.ForeignKey(
        Place,
        related_name='place_answered_id',
        null=True,
        blank=True,
        default=None)
    type = models.IntegerField(choices=QUESTION_TYPES)
    inserted = models.DateTimeField(default=datetime.now)
    response_time = models.IntegerField(default=0)
    options = models.ManyToManyField(Place)
    number_of_options = models.IntegerField(default=0)
    objects = AnswerManager()

    def save(self, update_model=False):
        if update_model:
            g = 1.0 / self.number_of_options if self.number_of_options != 0 else 0
            prediction = Answer.objects.predict(self.user, self.place_asked, g)
            result = self.place_asked == self.place_answered
            Answer.objects.update_model(self.user, self.place_asked, prediction, result)
        models.Model.save(self)

    def __unicode__(self):
        return (
            u'user: {0}, requested: {1}, answered: {2}, correct: {3}'.format(
                self.user, self.place_asked, self.place_answered, self.place_asked == self.place_answered)
        )

    class Meta:
        app_label = 'geography'
        ordering = ["-inserted"]
