# -*- coding: utf-8 -*-
from django.db import models
from place import Place
from django.contrib.auth.models import User
from math import exp, ceil


class UserPlaceManager(models.Manager):

    def for_user_and_map_prepared(self, user, map, lang_code):
        return self.raw("""
    SELECT
        geography_currentskill_prepared.user_id * 100000 + geography_placerelation.place_id AS dummy_id,
        geography_placerelation.place_id AS place_id,
        geography_currentskill_prepared.user_id AS user_id,
        geography_currentskill_prepared.currentskill AS currentskill,
        geography_currentskill_prepared.value AS skill,
        geography_place.type AS type,
        geography_place.name_""" + lang_code + """ AS name,
        geography_place.code AS code
    FROM
        geography_placerelation
        INNER JOIN geography_placerelation_related_places
            ON geography_placerelation.id =
                geography_placerelation_related_places.placerelation_id
        INNER JOIN geography_currentskill_prepared
            ON geography_placerelation_related_places.place_id =
                geography_currentskill_prepared.place_id
        INNER JOIN geography_place
            ON geography_place.id = geography_placerelation_related_places.place_id
    WHERE
        (geography_placerelation.type = 1 OR
        geography_placerelation.type = 4 ) AND
        geography_currentskill_prepared.user_id = %s AND
        geography_placerelation.place_id = %s
    ORDER BY
        geography_place.name;
        """, [user.id, map.place.id]
        )

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
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    place = models.ForeignKey(Place, on_delete=models.DO_NOTHING)
    skill = models.FloatField(default=0)

    objects = UserPlaceManager()

    def to_serializable(self):
        probability = 1.0 / (1 + exp(-self.skill))
        learned = probability > 0.9
        ret = {
            'code': self.code,
            'name': self.name,
            'skill': self.skill,
            'practiced': self.currentskill is not None and not learned,
            'learned': learned,
            'displayed': self.currentskill is not None or learned,
            'probability': ceil(10 * probability) / 10.0,
            'certainty': 1
        }
        return ret

    class Meta:
        app_label = 'geography'
        managed = False

    """ READ ONLY MODEL """
    def save(self, **kwargs):
        raise NotImplementedError
