# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
import elo
import logging
import place
LOGGER = logging.getLogger(__name__)


class AnswerManager(models.Manager):

    def get_success_rate(self, user, n):
        answers = self.filter(
            user=user,
        ).order_by("-inserted")[:n]
        return sum([a.place_asked_id == a.place_answered_id for a in answers]) / float(n)


class Answer(models.Model):
    ON_SAVE_LISTENERS = [elo.Elo.on_answer_save]
    FIND_ON_MAP = 1
    PICK_NAME = 2
    QUESTION_TYPES = (
        (FIND_ON_MAP, "find on map"),
        (PICK_NAME, "pick name")
    )
    user = models.ForeignKey(User)
    place_asked = models.ForeignKey(place.Place, related_name='place_asked_id')
    place_answered = models.ForeignKey(
        place.Place,
        related_name='place_answered_id',
        null=True,
        blank=True,
        default=None)
    type = models.IntegerField(choices=QUESTION_TYPES)
    inserted = models.DateTimeField(default=datetime.now)
    response_time = models.IntegerField(default=0)
    options = models.ManyToManyField(place.Place)
    number_of_options = models.IntegerField(default=0)
    objects = AnswerManager()

    def save(self, update_model=False):
        if update_model:
            for listener in Answer.ON_SAVE_LISTENERS:
                listener(self)
        models.Model.save(self)

    def __unicode__(self):
        return (
            u'user: {0}, requested: {1}, answered: {2}, correct: {3}'.format(
                self.user, self.place_asked, self.place_answered, self.place_asked == self.place_answered)
        )

    class Meta:
        app_label = 'geography'
        ordering = ["-inserted"]
