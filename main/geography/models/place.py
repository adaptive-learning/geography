# -*- coding: utf-8 -*-
from django.db import models
from django.template.defaultfilters import slugify
from django.core.cache import cache
from django.db import connection
import recommendation
import json
import random
import logging

LOGGER = logging.getLogger(__name__)


class WeghtedPlace:

    def __init__(self, code, name, weight):
        self.code = code
        self.name = name
        self.weight = weight


class PlaceManager(models.Manager):

    def get_places_to_ask(self, user, map_place, expected_probability, n, place_types, ab_env):
        strategy_name = ab_env.get_membership(
            recommendation.STRATEGIES.keys(),
            recommendation.DEFAULT_STRATEGY_NAME,
            Place.AB_REASON_RECOMMENDATION)
        strategy = recommendation.STRATEGIES[strategy_name]
        return strategy(user, map_place, expected_probability, n, place_types)

    def get_states_with_map(self):
        return [pr.place for pr in PlaceRelation.objects.filter(
            place__type=Place.STATE,
            type=PlaceRelation.IS_ON_MAP,
        ).select_related('place').order_by("place__name")]

    def get_continents(self):
        return self.filter(type=Place.CONTINENT)


class Place(models.Model):

    AB_REASON_RECOMMENDATION = 'reason_recommendation'

    UNKNOWN = 0
    STATE = 1
    CITY = 2
    WORLD = 3
    CONTINENT = 4
    RIVER = 5
    LAKE = 6
    REGION_CZ = 7
    BUNDESLAND = 8
    PROVINCE = 9
    REGION_IT = 10
    REGION = 11
    AUTONOMOUS_COMUNITY = 12
    MOUNTAINS = 13
    ISLAND = 14
    PLACE_TYPES = (
        (UNKNOWN, 'Unknown'),
        (STATE, 'State'),
        (CITY, 'City'),
        (WORLD, 'World'),
        (CONTINENT, 'Continent'),
        (RIVER, 'River'),
        (LAKE, 'Lake'),
        (REGION_CZ, 'Region_cz'),
        (BUNDESLAND, 'Bundesland'),
        (PROVINCE, 'Province'),
        (REGION_IT, 'Region_it'),
        (REGION, 'Region'),
        (AUTONOMOUS_COMUNITY, 'Autonomous_Comunity'),
        (MOUNTAINS, 'Mountains'),
        (ISLAND, 'Island'),
    )
    PLACE_TYPE_PLURALS = (
        (UNKNOWN, u'Neznámé'),
        (STATE, u'Státy'),
        (CITY, u'Města'),
        (WORLD, u'Svět'),
        (CONTINENT, u'Kontinenty'),
        (RIVER, u'Řeky'),
        (LAKE, u'Jezera'),
        (REGION_CZ, u'Kraje'),
        (BUNDESLAND, u'Spolkové Země'),
        (PROVINCE, u'Provincie'),
        (REGION_IT, u'Oblasti'),
        (REGION, u'Regiony'),
        (AUTONOMOUS_COMUNITY, u'Autonomní společenství'),
        (MOUNTAINS, u'Pohoří'),
        (ISLAND, u'Ostrovy'),
    )
    PLACE_TYPE_SLUGS = dict((t[1].upper(), t[0]) for t in PLACE_TYPES)
    PLACE_TYPE_SLUGS_LOWER = dict((t[0], slugify(t[1].lower())) for t in PLACE_TYPES)
    PLACE_TYPE_SLUGS_LOWER_REVERSE = dict((slugify(t[1].lower()), t[0]) for t in PLACE_TYPES)
    CATEGORIES = {
        'political': [
            STATE,
            CITY,
            REGION,
            PROVINCE,
            REGION_CZ,
            REGION_IT,
            AUTONOMOUS_COMUNITY,
            BUNDESLAND,
        ],
        'water': [
            RIVER,
            LAKE,
        ],
        'surface': [
            MOUNTAINS,
            ISLAND,
        ],
    }
    code = models.SlugField(
        max_length=100,
        db_index=True,
        unique=True)
    name = models.CharField(max_length=100)
    type = models.IntegerField(choices=PLACE_TYPES, default=UNKNOWN)

    objects = PlaceManager()

    def confusing_places(self, map_place, n):
        cache_key = "map" + str(map_place.id) + "-place" + str(self.id)
        places_json = cache.get(cache_key)
        if places_json is None:
            cursor = connection.cursor()
            cursor.execute(
                '''
                SELECT
                    geography_place.code,
                    geography_place.name,
                    COUNT(geography_answer.id) AS confusing_factor
                FROM
                    geography_place
                    LEFT JOIN geography_answer ON (
                        geography_answer.place_answered_id = geography_place.id
                        AND geography_answer.place_asked_id = %s)
                WHERE
                    geography_place.id IN (
                        SELECT
                            geography_placerelation_related_places.place_id
                        FROM
                            geography_placerelation
                            INNER JOIN geography_placerelation_related_places
                                ON placerelation_id = geography_placerelation.id
                        WHERE
                            geography_placerelation.place_id = %s
                            AND
                            geography_placerelation.type = %s
                    )
                    AND geography_place.id != %s
                    AND geography_place.type = %s
                    AND (geography_answer.place_asked_id != geography_answer.place_answered_id OR ISNULL(geography_answer.place_asked_id))
                GROUP BY geography_place.id
                ORDER BY
                    confusing_factor DESC, RAND() DESC
                LIMIT 8
                ''',
                [
                    int(self.id),
                    int(map_place.place.id),
                    int(PlaceRelation.IS_ON_MAP),
                    int(self.id),
                    int(self.type)
                ])
            json_places = json.dumps([(p[0], p[1], p[2]) for p in cursor.fetchall()])
            expire_days = 3
            # TODO: change expire_days to something like:
            # expire_days = places[0].confusing_factor / 2
            expire_seconds = 60 * 60 * 24 * expire_days
            cache.set(cache_key, json_places, expire_seconds)
            places_json = cache.get(cache_key)
        return [
            Place(code=p[0], name=p[1])
            for p in Place._weighted_choices(json.loads(places_json), n)
        ]

    def __unicode__(self):
        return u'{0} ({1})'.format(self.name, self.code)

    def to_serializable(self):
        return {
            'code': self.code,
            'name': self.name
        }

    @staticmethod
    def _weighted_choices(choices, n):
        chosen = []
        choices_set = set()
        for i in choices:
            choices_set.add(WeghtedPlace(i[0], i[1], i[2]))
        for i in range(int(n)):
            c = Place._weighted_choice(choices_set)
            chosen.append((c.code, c.name))
            choices_set.remove(c)
        return list(chosen)

    @staticmethod
    def _weighted_choice(choices):
        if not len(choices):
            raise Exception("The list 'choices' can't be empty.")
        total = sum(c.weight for c in choices)
        if total == 0:
            LOGGER.warn("choices don't have weights")
            return random.choice(list(choices))
        r = random.uniform(0, total)
        upto = 0
        for c in choices:
            if upto + c.weight > r:
                return c
            upto += c.weight
        assert False, "Shouldn't get here"

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
    IS_TOO_SMALL_ON_MAP = 4
    PLACE_RELATION_TYPES = (
        (IS_ON_MAP, 'Is On Map'),
        (IS_SUBMAP, 'Is Submap'),
        (HAVE_LAND_BORDER, 'Have Land Border'),
        (IS_TOO_SMALL_ON_MAP, 'Is Too Small On Map'),
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
