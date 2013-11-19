from django.db import models
from django.contrib.auth.models import User
from lazysignup.models import LazyUser


class UserManager(models.Manager):

    def convert_lazy_user(self, user):
        LazyUser.objects.filter(user=user).delete()
        user.username = self.get_unused_username(user)
        user.save()

    def is_username_present(self, username):
        if User.objects.filter(username=username).count():
            return True
        return False

    def is_lazy(self, user):
        if user.is_anonymous() or len(user.username) != 30:
            return False
        return bool(LazyUser.objects.filter(user=user).count() > 0)

    def is_named(self, user):
        return user.first_name and user.last_name

    def _get_unused_username(self, user):
        condition = True
        append = ""
        i = 2
        while condition:
            username = user.first_name + user.last_name + append
            condition = self.is_username_present(username)
            append = '{0}'.format(i)
            i = i + 1
        return username


class User(User):

    objects = UserManager()

    def __unicode__(self):
        return self.user.username

    def to_serializable(self):
        return {
            'username': self.user.username,
            'points': self.points,
        }

    class Meta:
        app_label = 'geography'
        managed = False

    """ READ ONLY MODEL """
    def save(self, **kwargs):
        raise NotImplementedError
