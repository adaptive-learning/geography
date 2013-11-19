# -*- coding: utf-8 -*-
from django.db import models
from place import Place
from django.contrib.auth.models import User
from math import exp


class UserPlaceManager(models.Manager):

    def for_user_and_map(self, user, map_place):
        return self.filter(
            user=user,
            place__in=map_place.related_places.all()
        ).select_related('place').order_by('place__name')

    def from_user_and_place(self, user, place):
        try:
            user_place = self.get(user=user, place=place)
        except UserPlace.DoesNotExist:
            user_place = UserPlace(
                user=user,
                place=place,
            )
        return user_place


class UserPlace(models.Model):

    dummy_id = models.CharField(primary_key=True, max_length=40)
    user = models.ForeignKey(User)
    place = models.ForeignKey(Place)
    skill = models.FloatField(default=0)

    objects = UserPlaceManager()

    def to_serializable(self):
        ret = self.place.to_serializable()
        ret.update({
            'skill': self.skill,
            'probability': 1.0 / (1 + exp(-self.skill)),
            'certainty': 1
        })
        return ret

    class Meta:
        app_label = 'geography'
        managed = False

    """ READ ONLY MODEL """
    def save(self, **kwargs):
        raise NotImplementedError
