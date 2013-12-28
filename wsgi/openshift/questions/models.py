# -*- coding: utf-8 -*-
from accounts.models import Student
from core.models import Place, PlaceRelation
from datetime import datetime
from django.db import models


class UsersPlaceManager(models.Manager):

    def from_student_and_place(self, student, place):
        try:
            usersPlace = UsersPlace.objects.get(user=student, place=place)
        except UsersPlace.DoesNotExist:
            usersPlace = UsersPlace(
                user=student,
                place=place,
            )
        return usersPlace

    def add_answer(self, a):
        usersPlace = self.from_student_and_place(a.user, a.place)
        usersPlace._add_answer(a)


def all_correct(users_places):
    incorrect = [up for up in users_places if up.skill < 1]
    return len(incorrect) == 0


def update_place_difficulty(place):
    usersPlaces = UsersPlace.objects.filter(place=place)
    skills = [up.correctlyAnsweredCount / float(up.askedCount)
              for up in usersPlaces]
    difficulty = sum(skills) / len(skills) if len(skills) > 0 else 0.5
    place.difficulty = int((1 - difficulty) * Place.DIFFICULTY_CONVERSION)


class UsersPlace(models.Model):
    user = models.ForeignKey(Student, db_index=True)
    place = models.ForeignKey(Place, db_index=True)
    askedCount = models.IntegerField(default=0)
    skill = models.FloatField(default=0)
    correctlyAnsweredCount = models.IntegerField(default=0)
    lastAsked = models.DateTimeField(default=datetime.now)
    first_asked = models.DateTimeField(default=datetime.now)
    objects = UsersPlaceManager()

    def similar_places_knowladge(self):
        map = PlaceRelation.objects.filter(
            related_places=self.place,
            type=PlaceRelation.IS_ON_MAP)[0]
        last_users_places = UsersPlace.objects.filter(
            user=self.user,
            place_id__in=map.related_places.all(),
        ).order_by("-lastAsked")[:10]
        correct = [up for up in last_users_places if up.skill == 1]
        if len(last_users_places) < 5:
            return 0
        knowladge = 1.0 * len(correct) / len(last_users_places)
        return knowladge

    def get_skill(self):
        skill = self.correctlyAnsweredCount / \
            float(self.askedCount) if self.askedCount > 0 else 0
        skill = round(skill, 2)
        return skill

    def get_certainty(self):
        # TODO: create a field instead of this method
        if self.askedCount >= 2 and self.correctlyAnsweredCount == self.askedCount:
            newCertainty = 1
        else:
            newCertainty = self.askedCount / 3.0
        notSeenFor = datetime.now() - max(self.lastAsked, datetime.now())
        knownFor = self.lastAsked - self.first_asked
        if float(notSeenFor.days) > 0:
            notSeenForRatio = min(
                1,
                0.9 *
                knownFor.days /
                float(
                    notSeenFor.days))
        else:
            notSeenForRatio = 1
        certainty = min(newCertainty, notSeenForRatio)
        certainty = round(certainty, 2)
        return certainty

    def _add_answer(self, a):
        self.askedCount += 1
        if (a.place == a.answer):
            self.correctlyAnsweredCount += 1
        self.lastAsked = datetime.now()
        self.skill = self.get_skill()
        self.save()
        update_place_difficulty(self.place)

    def __unicode__(self):
        return u'user: {0}, place: [{1}]'.format(self.user, self.place)

    def to_serializable(self):
        ret = self.place.to_serializable()
        ret.update({
            'skill': self.skill,
            'certainty': self.get_certainty(),
        })
        return ret

    class Meta:
        db_table = 'core_usersplace'  # TODO migrate lagacy db_table
        unique_together = ("user", "place")


class AnswerManager(models.Manager):

    def get_last_10_answers(self, user):
        return self.filter(
            user=user,
        ).order_by("-askedDate")[:10]


class Answer(models.Model):
    FIND_ON_MAP = 10
    PICK_NAME_OF_6 = 26
    FIND_ON_MAP_OF_6 = 16
    PICK_NAME_OF_4 = 24
    FIND_ON_MAP_OF_4 = 14
    PICK_NAME_OF_2 = 22
    FIND_ON_MAP_OF_2 = 12
    QUESTION_TYPES = (
        (FIND_ON_MAP, u"Vyber na mapě objekt"),
        (PICK_NAME_OF_6, u"Jak se jmenuje objekt zvýrazněný na mapě?"),
        (FIND_ON_MAP_OF_6, u"Ze šesti zvýrazněných objektů na mapě vyber"),
        (PICK_NAME_OF_4, u"Jak se jmenuje objekt zvýrazněný na mapě?"),
        (FIND_ON_MAP_OF_4, u"Ze čtyř zvýrazněných objektů na mapě vyber"),
        (PICK_NAME_OF_2, u"Jak se jmenuje objekt zvýrazněný na mapě?"),
        (FIND_ON_MAP_OF_2, u"Ze dvou zvýrazněných objektů na mapě vyber"),
    )
    user = models.ForeignKey(Student, db_index=True)
    place = models.ForeignKey(Place, related_name='place_id')
    answer = models.ForeignKey(
        Place,
        related_name='answer_id',
        null=True,
        blank=True,
        default=None)
    # TODO: change to PositiveSmallIntegerField
    type = models.IntegerField(choices=QUESTION_TYPES)
    askedDate = models.DateTimeField(default=datetime.now)
    msResposeTime = models.IntegerField(default=0)
    options = models.ManyToManyField(Place)
    objects = AnswerManager()

    def __unicode__(self):
        return (
            u'user: {0}, requested: {1}, answered: {2}, correct: {3}'.format(
                self.user, self.place, self.answer, self.place == self.answer)
        )

    class Meta:
        ordering = ["-askedDate"]
        db_table = 'core_answer'  # TODO migrate lagacy db_table


class ConfusedPlacesManager(models.Manager):
    map_cache = {}

    def was_confused(self, askedPlace, answeredPlace):
        if answeredPlace is None:
            return
        try:
            confused = self.get(asked=askedPlace, confused_with=answeredPlace)
        except ConfusedPlaces.DoesNotExist:
            confused = ConfusedPlaces(
                asked=askedPlace,
                confused_with=answeredPlace,
            )
        confused.level_of_cofusion += 1
        confused.save()

    def get_similar_to(self, place, map):
        if not map in self.map_cache:
            self.map_cache[map] = self.filter(
                asked__in=map.related_places.all(),
                confused_with__in=map.related_places.all(),
            ).select_related()
        confused = [c for c in self.map_cache[map] if c.asked == place]
        return [c.confused_with for c in confused]


class ConfusedPlaces(models.Model):
    asked = models.ForeignKey(Place, related_name='asked_id')
    confused_with = models.ForeignKey(Place, related_name='confused_with_id')
    level_of_cofusion = models.IntegerField(default=0)
    objects = ConfusedPlacesManager()

    class Meta:
        ordering = ["-level_of_cofusion"]
        db_table = 'core_confusedplaces'  # TODO migrate lagacy db_table
