# -*- coding: utf-8 -*-
from django.db import models
from place import Place
from django.contrib.auth.models import User
from math import exp


class MapSkillManager(models.Manager):

    def for_user(self, user):
        return self.raw("""
    SELECT
        geography_currentskill.user_id * 100000 + geography_placerelation.place_id AS dummy_id,
        geography_placerelation.place_id AS place_id,
        geography_place_related.type AS type,
        geography_currentskill.user_id AS user_id,
        AVG(geography_currentskill.value) AS skill,
        geography_place.name AS name,
        geography_place.code AS code,
        COUNT(geography_currentskill.value) AS count
    FROM
        geography_placerelation
        INNER JOIN geography_placerelation_related_places
            ON geography_placerelation.id =
                geography_placerelation_related_places.placerelation_id
        INNER JOIN geography_currentskill
            ON geography_placerelation_related_places.place_id =
                geography_currentskill.place_id
        INNER JOIN geography_place AS geography_place_related
            ON geography_place_related.id = geography_placerelation_related_places.place_id
        INNER JOIN geography_place
            ON geography_place.id = geography_placerelation.place_id
    WHERE
        (geography_placerelation.type = 1 OR
        geography_placerelation.type = 4 ) AND
        geography_currentskill.user_id = %s
    GROUP BY
        geography_placerelation.place_id,
        geography_currentskill.user_id,
        geography_place_related.type;
    ORDER BY
        geography_place.name
        """, [user.id]
        )


class MapSkill(models.Model):

    dummy_id = models.CharField(primary_key=True, max_length=40)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    place = models.ForeignKey(Place, on_delete=models.DO_NOTHING)
    skill = models.FloatField(default=0)
    count = models.IntegerField(default=0)
    type = models.IntegerField(default=0)

    objects = MapSkillManager()

    def to_serializable(self):
        ret = {
            'code': self.code,
            'name': self.name,
            'type': Place.PLACE_TYPE_SLUGS_LOWER[self.type],
            'skill': self.skill,
            'count': self.count,
            'probability': 1.0 / (1 + exp(-self.skill)),
            'certainty': 1
        }
        return ret

    class Meta:
        app_label = 'geography'
        managed = False

    """ READ ONLY MODEL """
    def save(self, **kwargs):
        raise NotImplementedError
