# -*- coding: utf-8 -*-
from django.db import models
from django.db import connection
import math
from datetime import datetime
from math import exp


class PlaceManager(models.Manager):

    def get_places_to_ask(self, user, map_place, expected_probability, n):
        expected_skill = - math.log((1 - expected_probability) / expected_probability)
        cursor = connection.cursor()
        cursor.execute(
            '''
            SELECT
                geography_place.*,
                geography_localskill_prepared.value as local_skill,
                (
                    ABS(geography_localskill_prepared.value - %s)
                    /
                    ABS(%s + SIGN(geography_localskill_prepared.value - %s) * 5)
                ) AS deviation,
                COUNT(geography_answer.id) AS number_of_answers,
                CASE
                    WHEN COALESCE(MIN(
                            UNIX_TIMESTAMP(\'''' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '''\')
                            -
                            UNIX_TIMESTAMP(geography_answer.inserted)
                        ) / 60, 10) > 3 THEN 0
                    ELSE 1
                END AS invalidity
            FROM
                geography_localskill_prepared
                LEFT JOIN geography_place
                    ON geography_place.id = geography_localskill_prepared.place_id
                LEFT JOIN geography_answer
                    ON geography_answer.user_id = geography_localskill_prepared.user_id
                    AND geography_answer.place_asked_id = place_id
            WHERE
                geography_place.id IN (
                    SELECT
                        geography_placerelation_related_places.place_id
                    FROM
                        geography_placerelation
                        INNER JOIN geography_placerelation_related_places
                            ON placerelation_id = geography_placerelation.id
                    WHERE geography_placerelation.place_id = %s
                )
                AND geography_localskill_prepared.user_id = %s
            GROUP BY
                geography_localskill_prepared.user_id, geography_localskill_prepared.place_id
            ORDER BY invalidity, deviation, RAND() ASC
            LIMIT %s;
            ''',
            [
                float(expected_skill),
                float(expected_skill),
                float(expected_skill),
                int(map_place.place.id),
                int(user.id),
                int(10)
            ]
        )
        dict_places = self.fetchall(cursor)
        return [
            (
                Place(id=d['id'], code=d['code'], name=d['name'], type=d['type']),
                1.0 / (1 + exp(-d['local_skill'])),
                d['number_of_answers']
            )
            for d in dict_places
        ]

    def get_states_with_map(self):
        return [pr.place for pr in PlaceRelation.objects.filter(
            place__type=Place.STATE,
            type=PlaceRelation.IS_ON_MAP,
        ).select_related('place').order_by("place__name")]

    def get_continents(self):
        return self.filter(type=Place.CONTINENT)

    def fetchall(self, cursor):
        "Returns all rows from a cursor as a dict"
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]


class Place(models.Model):
    UNKNOWN = 0
    STATE = 1
    CITY = 2
    WORLD = 3
    CONTINENT = 4
    RIVER = 5
    LAKE = 6
    REGION = 7
    BUNDESLAND = 8
    PROVINCE = 9
    PLACE_TYPES = (
        (UNKNOWN, 'Unknown'),
        (STATE, 'State'),
        (CITY, 'City'),
        (WORLD, 'World'),
        (CONTINENT, 'Continent'),
        (RIVER, 'River'),
        (LAKE, 'Lake'),
        (REGION, 'Region'),
        (BUNDESLAND, 'Bundesland'),
        (PROVINCE, 'Province'),
    )
    PLACE_TYPE_PLURALS = (
        (UNKNOWN, u'Neznámé'),
        (STATE, u'Státy'),
        (CITY, u'Města'),
        (WORLD, u'Svět'),
        (CONTINENT, u'Kontinenty'),
        (RIVER, u'Řeky'),
        (LAKE, u'Jezera'),
        (REGION, u'Kraje'),
        (BUNDESLAND, u'Spolkové Země'),
        (PROVINCE, u'Provincie'),
    )
    PLACE_TYPE_SLUGS = {t[1].upper(): t[0] for t in PLACE_TYPES}
    code = models.SlugField(
        max_length=100,
        db_index=True,
        unique=True)
    name = models.CharField(max_length=100)
    type = models.IntegerField(choices=PLACE_TYPES, default=UNKNOWN)

    objects = PlaceManager()

    def confusing_places(self, map_place, n):
        return Place.objects.raw(
            '''
            SELECT
                *,
                (
                    SELECT
                        COUNT(geography_answer.id)
                    FROM geography_answer
                    WHERE
                        geography_answer.place_asked_id != geography_answer.place_answered_id
                        AND (
                            ( geography_answer.place_asked_id = geography_place.id
                                AND geography_answer.place_answered_id = %s )
                            OR ( geography_answer.place_answered_id = geography_place.id
                                AND geography_answer.place_asked_id = %s )
                        )
                        AND geography_answer.number_of_options < 2
                ) AS confusing_factor
            FROM
                geography_place
            WHERE
                geography_place.id IN (
                    SELECT
                        geography_placerelation_related_places.place_id
                    FROM
                        geography_placerelation
                        INNER JOIN geography_placerelation_related_places
                            ON placerelation_id = geography_placerelation.id
                    WHERE geography_placerelation.place_id = %s
                )
                AND geography_place.id != %s
                AND geography_place.type = %s
            ORDER BY
                confusing_factor, RAND() ASC
            LIMIT %s
            ''',
            [int(self.id), int(self.id), int(map_place.place.id), int(self.id), int(self.type), int(n)])

    def __unicode__(self):
        return u'{0} ({1})'.format(self.name, self.code)

    def to_serializable(self):
        return {
            'code': self.code,
            'name': self.name
        }

    class Meta:
        app_label = 'geography'
        ordering = ['type', 'name']


class PlaceRelationManager(models.Manager):

    def get_bordering_places(self, place):
        try:
            pr = self.get(place=place, type=PlaceRelation.HAVE_LAND_BORDER)
            prs = self.filter(
                related_places__in=pr.related_places.all(),
                type=PlaceRelation.HAVE_LAND_BORDER)
            return (
                Place.objects.exclude(id=place.id).filter(
                    id__in=[p.place_id for p in prs])
            )
        except PlaceRelation.DoesNotExist:
            return Place.objects.filter(code="###")


class PlaceRelation(models.Model):
    IS_ON_MAP = 1
    IS_SUBMAP = 2
    HAVE_LAND_BORDER = 3
    PLACE_RELATION_TYPES = (
        (IS_ON_MAP, 'Is On Map'),
        (IS_SUBMAP, 'Is Submap'),
        (HAVE_LAND_BORDER, 'Have Land Border'),
    )
    place = models.ForeignKey(
        Place,
        db_index=True,
        related_name='place_id')
    related_places = models.ManyToManyField(Place)
    type = models.IntegerField(choices=PLACE_RELATION_TYPES, default=1)
    objects = PlaceRelationManager()

    class Meta:
        app_label = 'geography'
        unique_together = ('type', 'place')

    def __str__(self):
        return "Place Relation: " + str(self.place) + " [" + str(self.id) + "]"
