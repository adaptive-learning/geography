# -*- coding: utf-8 -*-
from django.db import models
from place import Place
from django.contrib.auth.models import User

LEARNED_PROB = 0.9


class MapSkillManager(models.Manager):

    def for_user(self, user):
        return self.raw("""
    SELECT
        geography_currentskill_prepared.user_id * 100000 + geography_placerelation.place_id AS dummy_id,
        geography_placerelation.place_id AS place_id,
        geography_place_related.type AS type,
        geography_currentskill_prepared.user_id AS user_id,
        geography_place.name AS name,
        geography_place.code AS code,
        AVG( LEAST(
            1/(1+EXP(-geography_currentskill_prepared.value)),
            %s)
        ) AS goal_probability,
        COUNT(geography_currentskill_prepared.value) AS count,
        COUNT( IF(
            1/(1+EXP(-geography_currentskill_prepared.currentskill)) >= %s,
            1,
            NULL
        )) AS learned,
        COUNT( IF(
            1/(1+EXP(-geography_currentskill_prepared.currentskill)) < %s,
            1,
            NULL
        )) AS practiced
    FROM
        geography_placerelation
        INNER JOIN geography_placerelation_related_places
            ON geography_placerelation.id =
                geography_placerelation_related_places.placerelation_id
        INNER JOIN geography_currentskill_prepared
            ON geography_placerelation_related_places.place_id =
                geography_currentskill_prepared.place_id
        INNER JOIN geography_place AS geography_place_related
            ON geography_place_related.id = geography_placerelation_related_places.place_id
        INNER JOIN geography_place
            ON geography_place.id = geography_placerelation.place_id
    WHERE
        (geography_placerelation.type = 1 OR
        geography_placerelation.type = 4 ) AND
        geography_currentskill_prepared.user_id = %s
    GROUP BY
        geography_placerelation.place_id,
        geography_currentskill_prepared.user_id,
        geography_place_related.type
    ORDER BY
        geography_place.name
        """, [LEARNED_PROB, LEARNED_PROB, LEARNED_PROB, user.id]
        )

    def for_user_and_map_and_type(self, user, map, type):
        skills = self.for_user(user)
        for s in skills:
            if s.place_id == map.place_id and s.type == type:
                return s


class MapSkill(models.Model):

    dummy_id = models.CharField(primary_key=True, max_length=40)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    place = models.ForeignKey(Place, on_delete=models.DO_NOTHING)
    learned = models.IntegerField(default=0)
    practiced = models.IntegerField(default=0)
    type = models.IntegerField(default=0)

    objects = MapSkillManager()

    def to_serializable(self):
        ret = {
            'code': self.code,
            'name': self.name,
            'type': Place.PLACE_TYPE_SLUGS_LOWER[self.type],
            'learned': self.learned,
            'practiced': self.practiced,
            'goal_probability': self.goal_probability,
            'certainty': 1
        }
        return ret

    class Meta:
        app_label = 'geography'
        managed = False

    """ READ ONLY MODEL """
    def save(self, **kwargs):
        raise NotImplementedError
