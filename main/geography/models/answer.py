# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
import knowledge
import logging
import place
import ab
import test

LOGGER = logging.getLogger(__name__)


class AnswerManager(models.Manager):

    def save_with_listeners(self, answer_dict):
        answer_dict['inserted'] = datetime.now()
        for listener in Answer.ON_SAVE_LISTENERS:
            try:
                listener(answer_dict)
            except Exception as e:
                LOGGER.error('exception thrown while processing listener for answer save, listener: {}, exception: {}, message: {}'.format(listener.__name__, type(e), str(e)))
        answer = Answer(
            user_id=answer_dict['user'],
            place_asked_id=answer_dict['place_asked'],
            place_answered_id=answer_dict.get('place_answered', None),
            place_map_id=answer_dict['place_map'],
            type=answer_dict['type'],
            response_time=answer_dict['response_time'],
            number_of_options=answer_dict['number_of_options'],
            ip_address=answer_dict.get('ip_address', None),
            inserted=answer_dict['inserted'],
            test=test.Test(id=answer_dict['test_id'] if 'test_id' in answer_dict else None))
        models.Model.save(answer)
        if len(answer_dict.get('options', [])) > 0:
            answer.options = place.Place.objects.filter(
                id__in=answer_dict['options'],
            )
        if len(answer_dict.get('ab_values', [])) > 0:
            answer.ab_values = ab.Value.objects.filter(
                id__in=answer_dict['ab_values'])
        models.Model.save(answer)
        LOGGER.debug("answered: %s", answer_dict)


class Answer(models.Model):
    ON_SAVE_LISTENERS = [knowledge.KnowledgeUpdater(knowledge.DatabaseEnvironment()).stream_answer]
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
    place_map = models.ForeignKey(
        place.Place,
        related_name='place_map_id',
        # because of the backward compatibility
        null=True,
        # required for new answers
        blank=False,
        default=None
    )
    ab_values = models.ManyToManyField(ab.Value)
    ip_address = models.CharField(max_length=39, null=True, blank=True, default=None)
    test = models.ForeignKey(test.Test, null=True, blank=True, default=None)
    objects = AnswerManager()

    def save(self, **kwargs):
        raise NotImplementedError('use Answer.objects.save_with_listeners instead')

    def __unicode__(self):
        return (
            u'user: {0}, requested: {1}, answered: {2}, correct: {3}'.format(
                self.user, self.place_asked, self.place_answered, self.place_asked == self.place_answered)
        )

    class Meta:
        app_label = 'geography'
        ordering = ["-id"]
