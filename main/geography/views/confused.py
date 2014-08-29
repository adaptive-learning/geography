# -*- coding: utf-8 -*-
from geography.utils import JsonResponse
from geography.models import Place
from django.db import connection


def confused(request):
    cursor = connection.cursor()
    cursor.execute('''
        SELECT
            geography_place.code as code,
            geography_place.name_''' + request.LANGUAGE_CODE + ''' AS name,
            geography_place.type as type,
            COUNT(
                IF(
                    geography_answer.place_answered_id != geography_answer.place_asked_id,
                    geography_answer.place_asked_id,
                    NULL
                )
            ) as mistake_count,
            COUNT(
                    geography_answer.place_asked_id
            ) as count,
            map_place.code AS map_code,
            map_place.name AS map_name
        FROM
            geography_answer
                INNER JOIN
            geography_place
                ON geography_answer.place_asked_id = geography_place.id
                INNER JOIN
            geography_place as map_place
                ON map_place.id = geography_answer.place_map_id
        WHERE
            geography_answer.user_id = %s
        GROUP BY
            geography_answer.place_asked_id
        HAVING
            mistake_count > 1
        ORDER BY
            mistake_count
            DESC
    ''', [request.user.id])
    response = cursor.fetchall()
    response = [{
        'code': r[0],
        'name': r[1],
        'type': Place.PLACE_TYPE_SLUGS_LOWER[r[2]],
        'mistake_count': r[3],
        'asked_count': r[4],
        'map_slug': r[5],
        'map_name': r[6],
    } for r in response]
    return JsonResponse(response)
