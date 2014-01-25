# -*- coding: utf-8 -*-
import place
from django.db import connection
from datetime import datetime
from math import exp

WEIGHT_PROBABILITY = 10
WEIGHT_NUMBER_OF_ANSWERS = 5
MAX_NUMBER_OF_ANSWERS = 10
DECREASE_NUMBER_OF_ANSWERS = 0.5
TIME_AGO_SHIFT = 120


def by_additive_function(user, map_place, expected_probability, n, place_type):
    if expected_probability < 0 or expected_probability > 1:
        raise Exception('target probability has to be in range [0,1] and was ' + str(expected_probability))
    cursor = connection.cursor()
    cursor.execute(
        '''
        SELECT
            geography_place.*,
            geography_elolocalskill_prepared.value as local_skill,
            COUNT(geography_answer.id) AS number_of_answers,
            COALESCE(MIN(
                UNIX_TIMESTAMP(\'''' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '''\')
                -
                UNIX_TIMESTAMP(geography_answer.inserted)
            ), 31536000) AS number_of_seconds_ago
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
        ORDER BY RAND() ASC
        LIMIT 100;
        ''',
        [
            int(map_place.place.id),
            int(place.PlaceRelation.IS_ON_MAP),
            int(place_type),
            int(user.id)
        ]
    )
    dict_places = fetchall(cursor)
    to_sort = []
    for p in dict_places:
        p['predicted_probability'] = 1.0 / (1 + exp(-p['local_skill']))
        p['fun_time_ago'] = from_time_ago(p['number_of_seconds_ago'])
        p['fun_previous_answers'] = from_previous_answers(p['number_of_answers'])
        p['fun_normed_prob_diff'] = from_normed_prob_diff(
            expected_probability, p['predicted_probability'])
        p['additive_function_result'] = (
            p['fun_time_ago'] +
            p['fun_previous_answers'] +
            p['fun_normed_prob_diff']
        )
        to_sort.append(p)
    to_sort.sort(key=lambda p: -p['additive_function_result'])
    return dicts_to_places(to_sort[:n])


def from_time_ago(seconds_ago):
    return - float(TIME_AGO_SHIFT) / max(seconds_ago, 1)


def from_previous_answers(previous_answers_num):
    return WEIGHT_NUMBER_OF_ANSWERS - DECREASE_NUMBER_OF_ANSWERS * min(previous_answers_num, MAX_NUMBER_OF_ANSWERS)


def from_normed_prob_diff(expected, given):
    diff = expected - given
    sign = 1 if diff > 0 else -1
    normed_diff = abs(diff) / abs(expected - 0.5 + sign * 0.5)
    return (1 - normed_diff) * WEIGHT_PROBABILITY


def dicts_to_places(dict_places):
    return [
        (place.Place(id=d['id'], code=d['code'], name=d['name'], type=d['type']), d)
        for d in dict_places
    ]


def fetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
