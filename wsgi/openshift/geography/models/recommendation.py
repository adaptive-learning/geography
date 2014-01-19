# -*- coding: utf-8 -*-
import place
import math
import elo
from django.db import connection
from datetime import datetime
from math import exp


def by_order(user, map_place, expected_probability, n, place_type):
    if expected_probability < 0 or expected_probability > 1:
        raise Exception('target probability has to be in range [0,1] and was ' + str(expected_probability))
    expected_skill = -math.log((1 - max(0.01, min(0.99, expected_probability))) / max(0.01, expected_probability))
    cursor = connection.cursor()
    cursor.execute(
        '''
        SELECT
            geography_place.*,
            geography_elolocalskill_prepared.value as local_skill,
            (
                ABS(geography_elolocalskill_prepared.value - %s)
                /
                ABS(%s + SIGN(geography_elolocalskill_prepared.value - %s) * %s)
            ) AS deviation,
            COUNT(geography_answer.id) AS number_of_answers,
            CASE
                WHEN COALESCE(MIN(
                        UNIX_TIMESTAMP(\'''' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '''\')
                        -
                        UNIX_TIMESTAMP(geography_answer.inserted)
                    ) / 60, 10) > 1 THEN 0
                ELSE 1
            END AS invalidity
        FROM
            geography_elolocalskill_prepared
            LEFT JOIN geography_place
                ON geography_place.id = geography_elolocalskill_prepared.place_id
            LEFT JOIN geography_answer
                ON geography_answer.user_id = geography_elolocalskill_prepared.user_id
                AND geography_answer.place_asked_id = place_id
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
            AND (geography_place.type = %s OR ''' + ("TRUE" if place_type == -1 else "FALSE") + ''')
            AND geography_elolocalskill_prepared.user_id = %s
        GROUP BY
            geography_elolocalskill_prepared.place_id
        ORDER BY invalidity, deviation, RAND() ASC
        LIMIT %s;
        ''',
        [
            float(expected_skill),
            float(expected_skill),
            float(expected_skill),
            elo.Elo.LOCAL_SKILL_EXTREM,
            int(map_place.place.id),
            int(place.PlaceRelation.IS_ON_MAP),
            int(place_type),
            int(user.id),
            int(n)
        ]
    )
    dict_places = fetchall(cursor)
    return [
        (
            place.Place(id=d['id'], code=d['code'], name=d['name'], type=d['type']),
            1.0 / (1 + exp(-d['local_skill'])),
            d['number_of_answers']
        )
        for d in dict_places
    ]


def fetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
