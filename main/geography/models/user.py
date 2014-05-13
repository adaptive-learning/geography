from django.contrib.auth.models import User
from lazysignup.models import LazyUser
from django.db import connection
from contextlib import closing


def convert_lazy_user(user):
    LazyUser.objects.filter(user=user).delete()
    user.username = get_unused_username(user)
    user.save()


def is_username_present(username):
    if User.objects.filter(username=username).count():
        return True
    return False


def is_lazy(user):
    if user.is_anonymous() or len(user.username) != 30:
        return False
    return bool(LazyUser.objects.filter(user=user).count() > 0)


def is_named(user):
    return user.first_name and user.last_name


def get_unused_username(user):
    condition = True
    append = ""
    i = 2
    while condition:
        username = user.first_name + user.last_name + append
        condition = is_username_present(username)
        append = '{0}'.format(i)
        i = i + 1
    return username


def get_points(user):
    with closing(connection.cursor()) as cursor:
        cursor.execute(
            '''
            SELECT
                COUNT(geography_answer.id)
            FROM
                geography_answer
            WHERE
                user_id = %s
                AND
                geography_answer.place_asked_id = geography_answer.place_answered_id
            ''', [user.id])
        return cursor.fetchone()[0]


def to_serializable(user):
    return {
        'username': user.username,
        'points': get_points(user),
    }
