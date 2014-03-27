# -*- coding: utf-8 -*-


def fetchone(cursor):
    "Returns o row from a cursor as a dict, or None"
    desc = cursor.description
    row = cursor.fetchone()
    return dict(zip([col[0] for col in desc], row))


def fetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
