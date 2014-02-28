# -*- coding: utf-8 -*-
from django.db import models
from place import Place
from math import exp


class AveragePlaceManager(models.Manager):

    def for_map(self, map_places):
        return self.filter(
            place__in=map_places,
        ).select_related('place').order_by('place__name')

    def from_place(self, place):
        try:
            average_place = self.get(place=place)
        except AveragePlace.DoesNotExist:
            average_place = AveragePlace(
                place=place,
            )
        return average_place


class AveragePlace(models.Model):

    dummy_id = models.CharField(primary_key=True, max_length=40)
    place = models.ForeignKey(Place, on_delete=models.DO_NOTHING)
    skill = models.FloatField(default=0)

    objects = AveragePlaceManager()

    def to_serializable(self):
        ret = self.place.to_serializable()
        ret.update({
            'skill': self.skill,
            'probability': 1.0 / (1 + exp(self.skill)),
            'certainty': 1
        })
        return ret

    class Meta:
        app_label = 'geography'
        managed = False

    """ READ ONLY MODEL """
    def save(self, **kwargs):
        raise NotImplementedError
