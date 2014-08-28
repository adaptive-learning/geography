# -*- coding: utf-8 -*-
from geography.utils import JsonResponse
from django.db import connection


def confused(request):
    cursor = connection.cursor()
    cursor.execute('''
        SELECT
            geography_place.code as code,
            geography_place.name_''' + request.LANGUAGE_CODE + ''' AS name,
            COUNT(
                IF(
                    geography_answer.place_answered_id != geography_answer.place_asked_id,
                    geography_answer.place_asked_id,
                    NULL
                )
            ) as mistake_count,
            COUNT(
                    geography_answer.place_asked_id
            ) as count
        FROM
            geography_answer
            INNER JOIN geography_place
                ON geography_answer.place_asked_id = geography_place.id
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
        'mistake_count': r[2],
        'asked_count': r[3],
    } for r in response]
    return JsonResponse(response)
