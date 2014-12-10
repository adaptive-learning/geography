from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.conf import settings
from django.utils import translation
from lazysignup.models import LazyUser
from django.db import connection, models
from contextlib import closing
from geography.models import Answer


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


def get_answered_count(user):
    with closing(connection.cursor()) as cursor:
        cursor.execute(
            '''
            SELECT
                COUNT(geography_answer.id)
            FROM
                geography_answer
            WHERE
                user_id = %s
            ''', [user.id])
        return cursor.fetchone()[0]


def to_serializable(user):
    return {
        'username': user.username,
        'points': get_points(user),
    }


def set_lang_from_last_answer(sender, user, request, **kwargs):
    try:
        latest_answer = Answer.objects.filter(user=user).latest('inserted')
        language_code = Answer.LANGUAGES[latest_answer.language][1]
        translation.activate(language_code)
        request.LANGUAGE_CODE = translation.get_language()
        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = language_code
        request.session['django_language'] = language_code
    except Answer.DoesNotExist:
        pass


user_logged_in.connect(set_lang_from_last_answer)


class UserProfileManager(models.Manager):
    def get_profile(self, user):
        try:
            profile = self.get(user=user)
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user)
            profile.save()
        return profile


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    send_emails = models.BooleanField(default=True)
    objects = UserProfileManager()

    class Meta:
        app_label = 'geography'
