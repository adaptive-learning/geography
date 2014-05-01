# -*- coding: utf-8 -*-
from django.db import models
from place import Place
from django.contrib.auth.models import User
from math import exp


class MapSkillManager(models.Manager):

    def for_user(self, user):
        return self.filter(
            user_id=user.id,
        ).select_related('place').order_by('place__name')


class MapSkill(models.Model):

    dummy_id = models.CharField(primary_key=True, max_length=40)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    place = models.ForeignKey(Place, on_delete=models.DO_NOTHING)
    skill = models.FloatField(default=0)
    count = models.IntegerField(default=0)
    type = models.IntegerField(default=0)

    objects = MapSkillManager()

    def to_serializable(self):
        ret = self.place.to_serializable()
        ret.update({
            'type': Place.PLACE_TYPE_SLUGS_LOWER[self.type],
            'skill': self.skill,
            'count': self.count,
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
